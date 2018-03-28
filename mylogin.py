import sys
import time
import myconfig
from simplepam import authenticate

class MyLogin:

	#def __init__(self):


	@classmethod
	def ask_password(self, chat_id, config):
		userconfig = config.getuser(chat_id)
		if userconfig == None or 'login_lastaccess' not in userconfig:
			return True, True # the second true stands for new user
		else:
			login_lastaccess = userconfig['login_lastaccess']
			now = int(time.time())
			if abs(login_lastaccess - now) < config.login_timeout:
				print('--> mylogin check last access ok')
				return False, False	# the second true stands for new user
			else:
				return True, False	# the second true stands for new user

	@classmethod
	def check_password(self, chat_id, config, password, msg):
		#if self.ask_password(chat_id, config) == False:
		#	return True
		#print(repr(password))
		#print(repr(password.encode("ascii")))
		#print(repr(password.encode("latin-1")))
		#print(repr(password.encode("utf-8")))
		if authenticate('mypi', password.encode("ascii")) == True:
			print('--> autentication ok')
			config.adduserkey(chat_id, 'login_lastaccess', msg['date'], save = True)
			return True
		else:
			print('--> autentication wrong')
			return False
