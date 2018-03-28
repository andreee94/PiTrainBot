import sys
import myconfig
import os.path
import os
import subprocess
from telebot import types
import asyncio
from TrainMonitor.TrainMonitor import viaggiatreno
from trainmanager import TrainManager
from trainutils import TrainUtils
from botutils import BotUtils
from commandabstract import CommandAbstract

class TrainCommand(CommandAbstract):

	commands = ['add', 'remove', 'delete', 'edit', 'info', 'infoall', 'help', 'state', 'status', 'critical', 'notcritical']
	command_name = 'train'
	command_prefix = command_name + ' '

	@classmethod
	def getCommandName(self): # method name
		return self.command_name

	@classmethod
	def usesSchedulePattern(self): # return help text to be sent
		return True

	@classmethod
	def requiresPassword(self):
		return False

	@classmethod
	def help(self):
		return 'All train commands are:\n' + "\n".join(self.commands)

	@classmethod
	def isCommand(self, config, text):
		return self.privateIsCommand(config, text, self.commands)

	@classmethod
	async def executeSchedule(self, sender, chat_id, config, msg, content_type, state_cmd, scheduler):
		params = state_cmd.split('|')
		trainNum = int(params[0])
		scheduler.event_now(('_trainmonitor', {'trainNum': trainNum, 'oldState':None, 'trainMsgID': None}))
		print('-----> Train ' + str(trainNum) + ' is SCHEDULED now')

	@classmethod
	async def execute(self, sender, chat_id, config, msg, content_type, state_cmd):
		if content_type != 'text': # TODO can also accept images
			await sender.sendMessage(self.wrongContent())
			return state_cmd

		stationName = None
		if state_cmd != None and state_cmd.startswith('wait_station'):
			await sender.sendMessage('Responce accepted.', reply_markup=BotUtils.markupRemoveKeyboard())
			stationName = msg['text'] # actual command text
			text = state_cmd.replace('wait_station|', '')
			print('wait_station '  + text)
			text = await self.prepareText(msg, sender, text = text)
		else:
			text = await self.prepareText(msg, sender)
		if text == None:
			return None

		print('--> Train command: ' + text)
		if state_cmd != None: print('--> Train state command: ' + state_cmd)

		wrong = False

		params = text.split(' ')
		if len(params) < 1:
			return
		cmd = params[0]
		print('cmd = ' + cmd)

		if cmd == 'add':
			state_cmd = await self.add(params, sender, chat_id, config, stationName)
		elif cmd == 'edit':
			state_cmd = await self.edit(params, sender, chat_id, config)
		elif cmd == 'state' or cmd == 'status':
			state_cmd = await self.state(params, sender, chat_id, config)
		elif cmd == 'info' and len(params) > 1:
			state_cmd = await self.info(params, sender, chat_id, config)
		elif (cmd == 'info' and len(params) == 1) or cmd == 'infoall':
			state_cmd = await self.infoAll(sender, chat_id, config)
		elif cmd == 'delete' or cmd == 'remove':
			state_cmd = await self.delete(params, sender, chat_id, config)

		if state_cmd != None:
			state_cmd += '|' + text

		# if not wrong:
		# 	return text
		# else:
		return state_cmd

	@classmethod
	def list_files_in_directory(self, dir):
		x = os.listdir(dir)
		return x

	@classmethod
	def trainExists(self, params, chat_id, config):
		trainNumber = params[1]
		trains = config.getuserkey(chat_id, 'trains')
		if trains == None:
			return False
		else: return trainNumber in trains
		# if 'trains' in userconfigs:
		# 	return (trainNumber in alltrains)
		#return False

	@classmethod
	async def add(self, params, sender, chat_id, config, stationName):
		# 0     |0   1    2		  3
		# train |add 4909 1234567 critical
		if len(params) < 2:
			await sender.sendMessage('Syntax of the command for train number 2620 on Monday, Wedneday, Thursday and setting it critical is:\nadd 2620 134 critical')
			return None
		if self.trainExists(params, chat_id, config):
			await sender.sendMessage('Train already added.\nUse edit to modify settings.')
		else:
			trainNum = params[1]
			# daysOfWeek = params[2]
			exists, isunique, stationsName, stationsID = await TrainUtils.existsAndUnique(trainNum)
			# if stationName != None:
			# 	print(stationName)
			# 	print(list(map(lambda x:x.lower(), stationsName)))
			if not exists:
				await sender.sendMessage('Train Number is wrong.')
				return None
			if isunique or stationName in stationsName:
				sName, sID = None, None
				if isunique:
					sName = stationsName
					sID = stationsID
				else:
					index = stationsName.index(stationName)
					sName = stationName
					sID = stationsID[index]

				train = {'stationName':sName, 'stationID':sID}
				if len(params) > 2:
					train['daysOfWeek'] = params[2]
				else: train['daysOfWeek'] = 'once'
				if len(params) > 3:
					train['priority'] = params[3]
				startingTime = TrainUtils.startingTimeTrain(await TrainUtils.getTrainStatus(trainNum, sID))
				if startingTime != None:
					train['startingTime'] = startingTime
				config.addTrain(chat_id, trainNum, train, save = True)
				await sender.sendMessage("Great! Train numer " + trainNum + ' that starts from ' + sName + ' is now monitored.')
				return 'must_schedule|' + str(trainNum)
			elif not isunique:
				markup = BotUtils.markupFromListKeyboard(stationsName)
				print(stationsName)
				print(markup)
				#markup = types.ForceReply(selective=True)
				await sender.sendMessage("Which is the starting station?", reply_markup=markup)
				return 'wait_station'
			return None

	@classmethod
	async def edit(self, params, sender, chat_id, config):
		# 0     |0    1    2		  3
		# train |edit 4909 1234567 critical
		if len(params) < 2:
			await sender.sendMessage('Syntax of the command for train number 2620 on Monday, Wedneday, Thursday and setting it critical is:\nedit 2620 134 critical')
			return None
		if not self.trainExists(params, chat_id, config):
			await sender.sendMessage('Train isn not added.\nUse add to start to track it.')
			return None
		else:
			trainNum = params[1]
			train = config.getTrain(chat_id, trainNum)
			if len(params) > 2:
				train['daysOfWeek'] = params[2]
			if len(params) > 3:
				train['priority'] = params[3]
			#import pdb; pdb.set_trace()
			trainStatus = await TrainUtils.getTrainStatus(trainNum, TrainManager.getStationID(train));
			startingTime = TrainUtils.startingTimeTrain(trainStatus)
			if startingTime != None:
				train['startingTime'] = startingTime
			if config.editTrain(chat_id, trainNum, train, save = True) != None:
				await sender.sendMessage('Train' + trainNum + ' edited correctly.')
		return None

	@classmethod
	async def delete(self, params, sender, chat_id, config):
		# 0     |0    1    2		  3
		# train |edit 4909 1234567 critical
		if len(params) < 2:
			await sender.sendMessage('Syntax of the command for train number 2620 is:\ndelete 2620')
			return None
		if not self.trainExists(params, chat_id, config):
			await sender.sendMessage('Train is not added.\nUse add to start to track it.')
			return None
		else:
			trainNum = params[1]
			train = config.getTrain(chat_id, trainNum)
			if config.delTrain(chat_id, trainNum, save = True) != None:
				await sender.sendMessage('Train' + trainNum + ' removed correctly.')
		return None

	@classmethod
	async def state(self, params, sender, chat_id, config):
		# 0     |0    1
		# train |state 4909
		if len(params) < 2:
			await sender.sendMessage('Syntax of the command for train number 2620 is:\nstate 2620\nstatus 2620')
			return None
		if not self.trainExists(params, chat_id, config):
			await sender.sendMessage('If you want to track regularly the train use command add')
		else:
			sID = TrainManager.getStationID(train)
			#return None

		trainNum = params[1]
		exists, isunique, stationsName, stationsID = await TrainUtils.existsAndUnique(trainNum)
		if not exists:
			await sender.sendMessage('Train Number is wrong.')
			return None
		if not isunique:
			await sender.sendMessage('More than one train with this number.\nYou can track it with add command')
			return None
		sID = stationsID

		train = config.getTrain(chat_id, trainNum)
		trainStatus = await TrainUtils.getTrainStatus(trainNum, sID)
		await sender.sendMessage(TrainUtils.printAllStations(trainStatus), parse_mode='Markdown')
		return None

	@classmethod
	async def info(self, params, sender, chat_id, config):
		# 0     |0    1
		# train |info 4909
		if not self.trainExists(params, chat_id, config):
			await sender.sendMessage('Train is not added.\nUse add to start to track it.')
			return None
		else:
			trainNum = params[1]
			train = config.getTrain(chat_id, trainNum)
			print(train)
			text = ''
			text += 'Train number: ' + str(trainNum) + '\n'
			if 'stationName' in train: text += 'Starting station: ' + train['stationName'] + '\n'
			if 'startingTime' in train: text += 'Starting at: ' + TrainUtils.format_timestamp(train['startingTime'], fmt='%H:%M') + '\n'
			if 'daysOfWeek' in train: text += 'Days of tracking: ' + TrainUtils.getDaysOfWeekFormatted(train['daysOfWeek']) + '\n'
			if 'priority' in train: text += 'Priority: ' + train['priority'] + '\n'
			await sender.sendMessage(text)
		return None

	@classmethod
	async def infoAll(self, sender, chat_id, config):
		trains = config.getuserkey(chat_id, 'trains')
		if len(trains) == 0:
			await sender.sendMessage('No trains monitored.')
		for t in trains:
			await self.info(['info', t], sender, chat_id, config)



			#
