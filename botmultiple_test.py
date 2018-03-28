
import sys
import asyncio
import trainutils
import time
import telepot
from telepot.aio.loop import MessageLoop
from telepot.aio.delegate import per_chat_id, create_open, create_run, pave_event_space
from myconfig import MyConfig
from mylogin import MyLogin
from usercommand import UserCommandDocs
from torrentcommand import TorrentCommand
from traincommand import TrainCommand
from trainmanager import TrainManager
from trainutils import TrainUtils

"""
$ python3.6 alarma.py <token>
Send a number which indicates the delay in seconds. The bot will send you an
alarm message after such a delay. It illustrates how to use the built-in
scheduler to schedule custom events for later.
To design a custom event, you first have to invent a *flavor*. To prevent flavors
from colliding with those of Telegram messages, events are given flavors prefixed
with `_` by convention. Then, follow these steps, which are further detailed by
comments in the code:
1. Customize routing table so the correct function gets called on seeing the event
2. Define event-handling function
3. Provide the event spec when scheduling events
"""


class MyChatHandler(telepot.aio.helper.ChatHandler):

	def __init__(self, *args, **kwargs):
		super(MyChatHandler, self).__init__(*args, **kwargs)
		self.commands = [UserCommandDocs, TorrentCommand, TrainCommand] #, TrainCommand]
		self.state = config.getuserkey(self.chat_id, 'state') # TODO load from file depending on chat id
		self.state_cmd = config.getuserkey(self.chat_id, 'state_cmd')

		# 1. Customize the routing table:
		#      On seeing an event of flavor `_alarm`, call `self.on__alarm`.
		# To prevent flavors from colliding with those of Telegram messages,
		# events are given flavors prefixed with `_` by convention. Also by
		# convention is that the event-handling function is named `on_`
		# followed by flavor, leading to the double underscore.
		self.router.routing_table['_trainmonitor'] = self.on__trainmonitor

		global initedIDs
		if self.chat_id not in initedIDs:
			initedIDs.append(self.chat_id)
			for t in config.getAllTrains(self.chat_id):
				#import pdb; pdb.set_trace()
				trainNum = t
				print('-----> Train ' + str(trainNum) + ' is SCHEDULED now.')
				oldState = config.getTrainKey(self.chat_id, trainNum, 'stateOld')
				trainMsgID = config.getTrainKey(self.chat_id, trainNum, 'trainMsgID')
				ev = self.scheduler.event_now(('_trainmonitor', {'trainNum': trainNum, 'oldState':oldState, 'trainMsgID':trainMsgID}))
				#print(ev)
				#event.append(ev)

	# 2. Define event-handling function
	async def on__trainmonitor(self, event):
		global config
		#import pdb; pdb.set_trace()
		trainNum = event['_trainmonitor']['trainNum']
		oldState = event['_trainmonitor']['oldState']
		trainMsgID = event['_trainmonitor']['trainMsgID']

		train, trainSettings = await TrainManager.getTrainStatusAndSettings(self.chat_id, trainNum, config)
		if train == None or trainSettings == None: #train removed
			return
		state, text, critical = TrainManager.manageTrainSend(self.chat_id,  train, trainSettings, oldState, self.sender, trainMsgID)
		nextSchedule, mustSend, mustRemove = TrainManager.manageTrainSchedule(self.chat_id, train, trainSettings, state)

		print('---------------------')
		#import pdb; pdb.set_trace()
		print('Source| space: ' + str(event['_trainmonitor']['source']['space']) + ' id: ' + str(event['_trainmonitor']['source']['id']))
		print('Monitoring train ' + str(trainNum))
		print('oldstate = ' + str(oldState))
		print('state = ' + str(state))
		print('now is ' + TrainUtils.format_timestamp(time.time() * 1000, fmt='%d -- %H:%M:%S,%MS'))
		if nextSchedule != None:
			print('nextSchedule is ' + TrainUtils.format_timestamp(nextSchedule * 1000))
		if text == None:
			print('text is ' + str(text))
		print('must send' + str(mustSend))
		print('msgID is ' + str(trainMsgID))

		if mustSend and text != None:
			trainMsgID = await TrainManager.sendOrEdit(self.sender, self.bot, self.chat_id, trainMsgID, text, critical)

		if nextSchedule != None:
			print('-----> Train ' + str(trainNum) + ' is SCHEDULED at ' + TrainUtils.format_timestamp(nextSchedule * 1000, fmt='%d -- %H:%M:%S,%MS'))
			self.scheduler.event_at(nextSchedule, ('_trainmonitor', {'trainNum': trainNum, 'oldState':state, 'trainMsgID': trainMsgID}))
		#else: self.scheduler.cancel(event)

		config.addTrainKey(self.chat_id, trainNum, 'stateOld', state)
		config.addTrainKey(self.chat_id, trainNum, 'trainMsgID', trainMsgID)
		print('msgID is ' + str(trainMsgID))

		if mustRemove:
			await self.sender.sendMessage('Train ' + str(trainNum) + ' is arrived.\nIt will be removed')
			config.delTrain(self.chat_id, trainNum, save=True)

		#print(event)  # see what the event object actually looks like
		#exists, isunique, stationsName, stationsID = trainutils.existsAndUnique(event['_alarm']['trainNum'])
		#await self.sender.sendMessage('Beep beep, time to wake up!' + stationsName)

	async def on_callback_query(self, msg):
		query_id, from_id, data = telepot.glance(msg, flavor='callback_query')
		print('Callback query:', query_id, from_id, data)

	async def on_chat_message(self, msg):
		print(telepot.message_identifier(msg))

		global config
		content_type, chat_type, chat_id = telepot.glance(msg)
		if content_type != 'text':
			if self.state == None:
				return
		else: text = msg['text']

		if self.state == None:
			if text.lower() == 'help': # and self.state == None:
				await self.sender.sendMessage(helpcommands(self.commands))
			elif text.lower() == 'where':
				await self.sender.sendMessage('No command is active.')
			else:
				for c in self.commands:
					if c.isCommandName(text):
						if c.requiresPassword():
							ask_password, self.new_user = MyLogin.ask_password(self.chat_id, config)
							if ask_password:
								self.state = 'wait_pwd'
								self.waiting_command = text
								print('--> password required.')
								await self.sender.sendMessage('Send Raspberry Pi password:')
							else:
								self.state = text
								await self.sender.sendMessage('Command started: ' + text)
								print('--> user already logged in.')
						else:
							self.state = text
							await self.sender.sendMessage('Command started: ' + text)
				if self.state == None: # no command found
					print('--> no command found.')
					await self.sender.sendMessage('The command does not exist.')
		elif self.state == 'wait_pwd':
			if text.lower() == 'quit' or text.lower() == 'exit' or text.lower() == 'cancel':
				await self.sender.sendMessage('Ready to start a new command.')
				self.state = None
				self.state_cmd = None
			elif MyLogin.check_password(chat_id, config, text, msg):
				#cannot delete user msg
				await self.sender.sendMessage('Password accepted!\nIt is suggested to delete the password message.')
				self.state = self.waiting_command
			else:
				if self.new_user: await self.sender.sendMessage('Wrong password.')
				else: await self.sender.sendMessage('Sessione expired.\nSend the correct password.')
		else:
			config.adduserkey(self.chat_id, 'lastaccess', msg['date'], True) # update last user access
			command_found = False
			if text.lower() == 'quit' or text.lower() == 'exit' or text.lower() == 'cancel':
				await self.sender.sendMessage('Exit from ' + self.state + ' command.')
				self.state = None
				self.state_cmd = None
			elif text.lower() == 'where':
				await self.sender.sendMessage('Command ' + self.state + ' is active.')
			else:
				for c in self.commands:
					if c.isCommandName(self.state):
						command_found = True
						print('--> state_cmd = ' + str(self.state_cmd))
						if text.lower() == 'help':
							await self.sender.sendMessage(c.help())
						elif self.state_cmd != None or c.isCommand(config, text):
							self.state_cmd = await c.execute(self.sender, self.chat_id, config, msg, content_type, self.state_cmd)
							print('--> command:' + text)
						if c.usesSchedulePattern():
							if self.state_cmd != None and self.state_cmd.startswith('must_schedule|'):
								self.state_cmd = self.state_cmd.replace('must_schedule|', '')
								await c.executeSchedule(self.sender, self.chat_id, config, msg, content_type, self.state_cmd, self.scheduler)
				if command_found == False:
					await self.sender.sendMessage('Not supported : ' + msg['text'])

		#if self.state != None:
			config.adduserkey(self.chat_id, 'state', self.state, save = False)
		#else: config.removeuserkey(self.chat_id, 'state', self.state, save = False)
		#if self.state_cmd != None:
			config.adduserkey(self.chat_id, 'state_cmd', self.state_cmd, save = True)
		#else: config.removeuserkey(self.chat_id, 'state_cmd', self.state_cmd, save = True)
		# try:
		#     delay = float(msg['text'])
		#
		#     # 3. Schedule event
		#     #      The second argument is the event spec: a 2-tuple of (flavor, dict).
		#     # Put any custom data in the dict. Retrieve them in the event-handling function.
		#     # delay = 10
		#     self.scheduler.event_later(delay, ('_trainmonitor_start', {'payload': delay, 'trainNum':4910}))
		#     await self.sender.sendMessage('Got it. Alarm is set at %.1f seconds from now.' % delay)
		# except ValueError:
		#     await self.sender.sendMessage('Not a number. No alarm set.')

def helpcommands(commands):
	text = 'The available commands are:'
	for c in commands:
		text += '\n-->' + c.getCommandName()
	text += '\nType \'where\' to know which command is active.'
	return text.strip()

global config
config = MyConfig()
config.load()

TOKEN = config.token #sys.argv[1]

global initedIDs
initedIDs = []

bot = telepot.aio.DelegatorBot(TOKEN, [
	pave_event_space()(
		[per_chat_id()], create_open, MyChatHandler, timeout=10),
])

loop = asyncio.get_event_loop()
loop.create_task(MessageLoop(bot).run_forever())
print('Listening ...')

loop.run_forever()
