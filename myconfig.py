import json
import sys
import os.path

class MyConfig:

	def __init__(self):
		self.userchats = {k: [] for k in range(1)}
		self.filename = "config.json"
		self.token = ''
		self.login_timeout = 600 # 10 min

	#def init():
	#	self.filename = "config.json"
	#	self.token = '';

	def load(self):
		with open(self.filename, 'r') as f:
   			self.config = json.load(f)
		self.token = self.getfromconfig('token')
		self.login_timeout =  self.getfromconfig('login_timeout')
		self.loadAllUsers()
		#self.login_lastaccess =  self.getfromconfig('login_lastaccess')
		#self.token = config['token']
		#print(config['andrea'])

	def update(self):
		self.login_lastaccess =  self.getfromconfig('login_lastaccess')

	def getfromconfig(self, name, else_value = None):
		#print(self.config)
		if name in self.config:
			return self.config[name]
		else:
			return else_value

	def add(self, key, value, save = True):
		self.config[key] = value
		self.update()
		if save:
			self.save()

	def save(self):
		with open(self.filename, 'w') as f:
			json.dump(self.config, f,indent=3)

	def saveuser(self, chat_id):
		with open(MyConfig.getuserjson(chat_id), 'w+') as f:
			json.dump(self.userchats[str(chat_id)], f)

	# def adduser(self, chat_id, key, value, save = True):
	# 	#with open('/userchats/' + chat_id + '.json', 'ab+') as f:
   	# 	#	self.userchats = json.load(f)
	# 	if str(chat_id) in self.userchats and key in self.userchats[str(chat_id)]:
	# 		self.userchats[str(chat_id)][key] = value
	# 	else:
	# 		self.userchats[str(chat_id)] = {key : value}
	# 	if save:
	# 		self.saveuser(chat_id)

	def adduserkey(self, chat_id, key, value, save = True):
		if str(chat_id) in self.userchats: # and key in self.userchats[str(chat_id)]:
			self.userchats[str(chat_id)][key] = value
		else:
			self.userchats[str(chat_id)] = {key : value}
		if save:
			self.saveuser(chat_id)

	def removeuserkey(self, chat_id, key, value, save = True):
		if str(chat_id) in self.userchats: # and key in self.userchats[str(chat_id)]:
			if key in self.userchats[str(chat_id)]:
				self.userchats[str(chat_id)].pop(key)
		if save:
			self.saveuser(chat_id)

	def getuser(self, chat_id):
		if os.path.isfile(MyConfig.getuserjson(chat_id)):
			#print('--> getuser() -- ' + MyConfig.getuserjson(chat_id))
			with open(MyConfig.getuserjson(chat_id), 'r') as f:
				return json.load(f)
		else:
			return None

	def getuserkey(self, chat_id, key, default = None):
		userconfig = self.getuser(chat_id)
		if userconfig != None:
			self.userchats[str(chat_id)] = userconfig
			if key in userconfig:
				return userconfig[key]
		return default

	def getuserprivatefile(self, chat_id, file_type):
		if file_type == 'path':
			return self.getuserfolder(chat_id) + 'documents/'
		elif file_type == 'codice_fiscale':
			if file_type in self.userchats[str(chat_id)]:
				return getuserkey(chat_id, file_type)
			else: return 'Not available yet.'
		else:
			return self.config['user']['codice_fiscale']

	def getAllUsers(self):
		users = []
		for u in list_files_in_directory('userchats/'):
			users.append(u)
			#users.append(u.replace('.json', ''))

	def getAllTrains(self, chat_id):
		return self.getuserkey(chat_id, 'trains')

	def loadAllUsers(self):
		users = []
		for u in self.list_files_in_directory('userchats/'):
			print('--> ' + u)
			chat_id = int(u)
			userconfig = self.getuser(chat_id)
			self.userchats[str(chat_id)] = userconfig

	def addTrain(self, chat_id, trainNum, train, save = True):
		if str(chat_id) in self.userchats:
			if not 'trains' in self.userchats[str(chat_id)]:
				self.userchats[str(chat_id)]['trains'] = {}
		else: self.userchats[str(chat_id)] = {'trains' : {}}

		self.userchats[str(chat_id)]['trains'][str(trainNum)] = train
		if save: self.saveuser(chat_id)

	def editTrain(self, chat_id, trainNum, train, save = True):
		if str(chat_id) in self.userchats:
			if 'trains' in self.userchats[str(chat_id)]:
				if str(trainNum) in self.userchats[str(chat_id)]['trains']:
					self.userchats[str(chat_id)]['trains'][str(trainNum)] = train
					if save: self.saveuser(chat_id)
					return True
		return None

	def getTrain(self, chat_id, trainNum):
		if str(chat_id) in self.userchats:
			if 'trains' in self.userchats[str(chat_id)]:
				if str(trainNum) in self.userchats[str(chat_id)]['trains']:
					return self.userchats[str(chat_id)]['trains'][str(trainNum)]

	def delTrain(self, chat_id, trainNum, save = True):
		if str(chat_id) in self.userchats:
			if 'trains' in self.userchats[str(chat_id)]:
				if str(trainNum) in self.userchats[str(chat_id)]['trains']:
					self.userchats[str(chat_id)]['trains'].pop(str(trainNum))
					if save: self.saveuser(chat_id)
					return True
		return None

	def addTrainKey(self, chat_id, trainNum, key, value, save = True):
		if str(chat_id) in self.userchats:
			if 'trains' in self.userchats[str(chat_id)]:
				if str(trainNum) in self.userchats[str(chat_id)]['trains']:
					self.userchats[str(chat_id)]['trains'][str(trainNum)][key] = value
					if save: self.saveuser(chat_id)

	def getTrainKey(self, chat_id, trainNum, key, save = True):
		if str(chat_id) in self.userchats:
			if 'trains' in self.userchats[str(chat_id)]:
				if str(trainNum) in self.userchats[str(chat_id)]['trains']:
					if key in self.userchats[str(chat_id)]['trains'][str(trainNum)]:
						return self.userchats[str(chat_id)]['trains'][str(trainNum)][key]
		return None

	@classmethod
	def getuserjson(self, chat_id):
		return self.getuserfolder(chat_id) + str(chat_id) + '.json'

	@classmethod
	def getuserfolder(self, chat_id):
		folder =  'userchats/' + str(chat_id) + '/'
		if not os.path.exists(folder):
			print('--> create folder: ' + folder)
			os.makedirs(folder)
		return folder

	@classmethod
	def list_files_in_directory(self, dir):
		x = os.listdir(dir)
		print('x')
		return x





#edit the data
#config['keytest'] = 'value'

#write it back to the file
#with open('config.json', 'w') as f:
#    json.dump(config, f)
