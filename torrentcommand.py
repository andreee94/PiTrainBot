import sys
import myconfig
import os.path
import os
import asyncio
import subprocess
from commandabstract import CommandAbstract

class TorrentCommand(CommandAbstract):

	#def __init__(self):

	commands = ['pause', 'resume', 'stop', 'start', 'getall', 'info', 'downloaded', 'status', 'help']
	complete_folder = '/media/pi/hdd/torrent/complete/'

	command_name = 'torrent'
	command_prefix = command_name + ' '

	@classmethod
	def getCommandName(self): # method name
		return TorrentCommand.command_name

	@classmethod
	def usesSchedulePattern(self): # return help text to be sent
		return False

	@classmethod
	def requiresPassword(self):
		return True

	@classmethod
	def help(self):
		return 'All the torrent commands are:\n' + "\n".join(TorrentCommand.commands)

	@classmethod
	def isCommand(self, config, text):
		return self.privateIsCommand(config, text, self.commands)

	# @classmethod
	# def isCommand(self, config, text):
	# 	text = text.lower()
	# 	if  text.startswith(TorrentCommand.command_name): # in TorrentCommand.commands
	# 		text = text.replace(TorrentCommand.command_prefix, '')
	# 		print('--> checking torrent command')
	# 		if text in TorrentCommand.commands:
	# 			return True
	# 		else: return False
	# 	else:
	# 		for c in TorrentCommand.commands:
	# 			if text.startswith(c):
	# 				return True
	# 	return False


	@classmethod
	async def execute(self, sender, chat_id, config, msg, content_type, state_cmd):
		if content_type != 'text':
			await sender.sendMessage(self.wrongContent())
			return state_cmd

		text = await self.prepareText(msg, sender)
		if text == None:
			return None

		wrong = False

		if text == 'downloaded':
			for f in TorrentCommand.list_files_in_directory(self.complete_folder):
				await sender.sendMessage(f)
		elif text in TorrentCommand.commands[0:2]: #'pause', 'resume', 'stop'
			if not TorrentCommand.is_deluge_running():
				await sender.sendMessage('Deluge is not running.')
			else: await TorrentCommand.deluge_action(text, sender)
		elif text == 'start':
			if  TorrentCommand.is_deluge_running():
				await sender.sendMessage('Deluge is already running.')
			else: await TorrentCommand.deluge_action(text, sender)
		elif text == 'getall' or text == 'info':
			if not TorrentCommand.is_deluge_running():
				await sender.sendMessage('Deluge is not running.')
			else: await TorrentCommand.deluge_info(sender)
		elif text == 'status':
			if  TorrentCommand.is_deluge_running():
				await sender.sendMessage('Deluge is running.')
			else: await sender.sendMessage('Deluge is not running.')
		elif text == 'help' or len(text) == 0:
			await sender.sendMessage(self.help())
		else:
			wrong = True
			await sender.sendMessage(self.wrongCommand())

		if not wrong:
			return text
		else: return state_cmd

	@classmethod
	def list_files_in_directory(self, dir):
		x = os.listdir(dir)
		return x

	@classmethod
	def is_deluge_running(self):
		output = subprocess.Popen("ps x |grep -v grep |grep -c \"deluged\"", shell=True, stdout=subprocess.PIPE).communicate()[0]
		#the result is in this format
		return output == b'1\n'
		#print(output)
		#output = str(output) #.encode("utf-8")
		#output = output.replace('\n', '')
		#print(output == b'1\n')
		#print(output.encode("utf-8"))
		#print(output.encode("ascii"))
		#print(subprocess.check_output('ps x |grep -v grep |grep -c \"deluged\"')) #, shell=True)
		#output = ps.communicate()[0]
		#print(output)
		#return output

	@classmethod
	async def deluge_info(self, sender):
		output = subprocess.Popen("deluge-console \"connect localhost:58846; info; quit\"", shell=True, stdout=subprocess.PIPE).communicate()[0]
		stroutput = output.decode("utf-8")
		stroutput_array = stroutput.split('\n \n')
		for s in stroutput_array:
			# print('--> ' + s)
			await sender.sendMessage(s)

	@classmethod
	async def deluge_action(self, text, sender):
		if text == 'stop':
			subprocess.call(['pkill', 'deluge'])
		elif text == 'start':
			subprocess.call(['deluged'])
		elif text == 'pause':
			subprocess.call("deluge-console \"connect localhost:58846; pause *; quit\"", shell = True)
		elif text == 'resume':
			subprocess.call("deluge-console \"connect localhost:58846; resume *; quit\"", shell = True)
		await sender.sendMessage('Command executed.')

	@classmethod
	async def check_send_file(self, sender, file):
		print(file)
		print(repr(file))
		file = file.encode("utf-8")
		if os.path.isfile(file):
			#bot.sendPhoto(chat_id, file)
			await sender.sendPhoto(open(file, 'rb'))
		else: await sender.sendMessage('The file is not available')
