import sys
import time
import telepot
from myconfig import MyConfig
from mylogin import MyLogin
from usercommand import UserCommandDocs
from torrentcommand import TorrentCommand
from telepot.loop import MessageLoop
from simplepam import authenticate

def handle(msg):
	content_type, chat_type, chat_id = telepot.glance(msg)
	print(content_type, chat_type, chat_id)

	#global is_checking_pwd
	wait_pwd = False

	ask_password, new_user = MyLogin.ask_password(chat_id, config)

	if ask_password:
		wait_pwd = True

	if wait_pwd == True:
		if content_type == 'text': # if not text wait for text
			#is_checking_pwd = True
			if MyLogin.check_password(chat_id, config, msg['text'], msg):
				wait_pwd = False
				bot.sendMessage(chat_id, 'Password accepted!\nIt is suggested to delete the password message.')
				#cannot delete msg
				#bot.deleteMessage(telepot.message_identifier(msg))
			else:
				if new_user: bot.sendMessage(chat_id, 'Password Errata.')
				else: bot.sendMessage(chat_id, 'Sessione Scaduta.')
			#is_checking_pwd = False
	else: #if wait_pwd == False:
		# update last timestamp depending on the last message
		config.adduser(chat_id, 'login_lastaccess', msg['date'], True)
		if content_type == 'text':
			if UserCommandDocs.isCommand(config, msg['text']):
				UserCommandDocs.execute(chat_id, config, msg['text'], bot)
			elif TorrentCommand.isCommand(config, msg['text']):
				TorrentCommand.execute(chat_id, config, msg['text'], bot)
			else: bot.sendMessage(chat_id, 'Not supported : ' + msg['text'])

	ask_password, new_user = MyLogin.ask_password(chat_id, config)
	if ask_password:
		print('ask password')
		bot.sendMessage(chat_id, 'Send Raspberry Pi password:')
		wait_pwd = True
############################################################
#global is_checking_pwd
#is_checking_pwd  = False
#MyConfig.init()
config = MyConfig()
config.load()
#config.save()

# It works
#print(authenticate('pi', 'wrong'))
#print(authenticate('pi', 'error'))

#print('main')
#print('kate')
print(config.token)

TOKEN = config.token
#TOKEN = sys.argv[1]  # get token from command-line

bot = telepot.Bot(TOKEN)
MessageLoop(bot, handle).run_as_thread()
print ('Listening ...')

# Keep the program running.
while 1:
    time.sleep(10)
