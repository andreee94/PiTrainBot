from abc import ABC, abstractmethod
from abc import ABCMeta
import asyncio

class abstractclassmethod(classmethod):

	__isabstractmethod__ = True

	def __init__(self, callable):
		callable.__isabstractmethod__ = True
		super(abstractclassmethod, self).__init__(callable)


# just a non working test
class CommandAbstract:

	@abstractclassmethod
	def requiresPassword(self): # return if the command is private or not
		raise NotImplementedError

	@classmethod
	def isCommandName(self, text):
		return text.lower() == self.getCommandName()

	# @property
	@abstractclassmethod
	def getCommandName(self): # method name
		raise NotImplementedError

	# @abstractclassmethod
	# def isCommand(self, config, text): # check if the text start the command
	#     raise NotImplementedError

	@classmethod
	def privateIsCommand(self, config, text, commands):
		print('--> checking command ' + self.getCommandName() + ': ' + text)
		text = text.lower()
		if  text.startswith(self.getCommandName()): # in TorrentCommand.commands
			text = text.replace(self.getCommandName() + ' ', '')

		for c in commands:
			if text.startswith(c):
				return True
		return False

	@abstractclassmethod
	def isCommand(self, config, text):
		raise NotImplementedError

	# @property
	@abstractclassmethod
	def help(self): # return help text to be sent
		raise NotImplementedError

	@classmethod
	async def prepareText(self, msg, sender, text = None): # return help text to be sent
		if text == None:
			text = msg['text']

		text = text.lower()
		if text == self.command_name: # if no command or space launch help
			await sender.sendMessage(self.help())
			return None
		if text.startswith(self.command_prefix):
			text = text.replace(self.command_prefix, '')
		text = text.strip()
		return text

	@classmethod
	def wrongCommand(self): # return help text to be sent
		return 'The command has a wrong syntax.\nType help to see available commands.'

	@classmethod
	def wrongContent(self): # return help text to be sent
		return 'The command does not support this content type.'

	@abstractclassmethod
	def usesSchedulePattern(self): # return help text to be sent
		raise NotImplementedError

	@abstractclassmethod
	async def execute(self, sender, chat_id, config, msg, content_type, state_cmd):
		raise NotImplementedError

	@abstractclassmethod
	async def executeSchedule(self, sender, chat_id, config, msg, content_type, state_cmd, scheduler):
		raise NotImplementedError




	#
