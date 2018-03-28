import sys
import myconfig
import os.path
from commandabstract import CommandAbstract

class UserCommandDocs(CommandAbstract):

	#def __init__(self):

	commands = ['ci', 'carta identita', 'carta d\'identita',
				'cf', 'codice fiscale', 'abbonamento', 'patente', 'help']

	command_name = 'user'
	command_prefix = command_name + ' '

	@classmethod
	def getCommandName(self): # method name
		return UserCommandDocs.command_name

	@classmethod
	def usesSchedulePattern(self): # return help text to be sent
		return False

	@classmethod
	def requiresPassword(self):
		return True

	@classmethod
	def help(self):
		return 'All user commands are:\n' + "\n".join(UserCommandDocs.commands)

	@classmethod
	def isCommand(self, config, text):
		return self.privateIsCommand(config, text, self.commands)

	# @classmethod
	# def isCommand(self, config, text):
	# 	if  text.lower().startswith(UserCommandDocs.command_prefix): # in TorrentCommand.commands
	# 		text = text.lower()
	# 		text = text.replace(UserCommandDocs.command_prefix, '')
	# 		print('checking user command')
	# 		if text in UserCommandDocs.commands:
	# 			return True
	# 		else: return False
	# 	return False
	# 	#if  text.lower() in UserCommandDocs.commands:
	# 	#	return True
	# 	#return False


	@classmethod
	async def execute(self, sender, chat_id, config, msg, content_type, state_cmd):
		if content_type != 'text': # TODO can also accept images
			await sender.sendMessage(self.wrongContent())
			return state_cmd

		text = await self.prepareText(msg, sender)
		if text == None:
			return None

		wrong = False

		path = config.getuserprivatefile(chat_id, 'path')
		ci_file = config.getuserprivatefile(chat_id, 'ci')
		cf_file = config.getuserprivatefile(chat_id, 'codice_fiscale')
		abbonamento_file = config.getuserprivatefile(chat_id, 'abbonamento')
		patente_file = config.getuserprivatefile(chat_id, 'patente')

		# path = config.config['user']['path']
		# ci_file = config.config['user']['ci']
		# cf_file = config.config['user']['codice_fiscale']
		# abbonamento_file = config.config['user']['abbonamento']
		# patente_file = config.config['andrea']['patente']
		print(text)
		if text in UserCommandDocs.commands[0:2]:
			await UserCommandDocs.check_send_file(sender, path + ci_file)
		elif text in UserCommandDocs.commands[3:4]:
			await sender.sendMessage(cf_file)
		elif text in UserCommandDocs.commands[5]:
			await UserCommandDocs.check_send_file(sender, path + abbonamento_file)
		elif text in UserCommandDocs.commands[6]:
			await UserCommandDocs.check_send_file(sender, path + patente_file)
		elif text == 'help' or text.len() == 0:
			await sender.sendMessage('All user commands are:\n' + "\n".join(UserCommandDocs.commands))
		else:
			wrong = True
			await sender.sendMessage(self.wrongCommand())

		if not wrong:
			return text
		else: return state_cmd


	@classmethod
	async def check_send_file(self, sender, file):
		print(file)
		print(repr(file))
		file = file.encode("utf-8")
		if os.path.isfile(file):
			#bot.sendPhoto(chat_id, file)
			await sender.sendPhoto(open(file, 'rb'))
		else: await sender.sendMessage('The file is not available yet.')
