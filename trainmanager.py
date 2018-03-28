from trainutils import TrainUtils
import time
import datetime
import sys
import myconfig
import os.path
import os
import subprocess
from telebot import types
from telepot.exception import TelepotException
import asyncio

class TrainManager:

	preScheduleTime = 3*60 # 3 minutes

	@classmethod
	def manageTrainSend(self, chat_id, train, trainSettings, oldState, sender, trainMsgID):
		#trainSettings = config.getTrain(chat_id, trainNum)
		#stationID = self.getStationID(trainSettings)
		#train = TrainUtils.getTrainStatus(trainNum, stationID)
		state = oldState # notstarted preschedule arrived cancelled nameofcurrentstation
		text = None

		if not TrainUtils.isTrainStarted(train):
			if self.isInPreSchedule(train):
				return 'preschedule', None, TrainManager.isCritical(trainSettings)
			else: return 'notstarted', None, TrainManager.isCritical(trainSettings)

		if TrainUtils.isTrainCancelled(train):
			state = 'cancelled'
			if oldState == None or oldState != 'cancelled':
				text = TrainUtils.printTrainCancelled(train)
			#trainMsgID = await self.sendOrEdit(sender, trainMsgID, text, self.isCritical(trainSettings))
		elif TrainUtils.isTrainArrived(train):
			state = 'arrived'
			if oldState != 'arrived':
				text = TrainUtils.printTrainArrived(train)
			#else: #TODO program scheduler for next day
				#trainMsgID = await self.sendOrEdit(sender, trainMsgID, text, self.isCritical(trainSettings))
		else:
			currentStation = TrainUtils.currentStation(train)
			if currentStation != None:
				currentStationName = currentStation['stazione']
			else: currentStationName = None
			if currentStationName != None and oldState != currentStationName:
				state = currentStationName
				text = TrainUtils.printAllStations(train)
				#trainMsgID = await self.sendOrEdit(sender, trainMsgID, text, self.isCritical(trainSettings))
			#else: state = oldState

		return state, text, TrainManager.isCritical(trainSettings)#, trainMsgID

	@classmethod
	def manageTrainSchedule(self, chat_id, train, trainSettings, state):
		#trainSettings = config.getTrain(chat_id, trainNum)
		#stationID = self.getStationID(trainSettings)
		#train = TrainUtils.getTrainStatus(trainNum, stationID)
		nextSchedule = None
		mustSend = False
		mustRemove = False
		if state == 'notstarted' or state == 'arrived':
			nextSchedule, diff = self.getNextDayDate(train, trainSettings)
			if diff != None:
				preSchedule = self.preScheduleTime #preSchedule = datetime.timedelta(0, 3 * 60)
				if nextSchedule != None:
					nextSchedule -= preSchedule
				else:
					if state == 'arrived': mustRemove = True
				if state == 'arrived': mustSend = True
			else: # should not happen but it happens
				mustSend = False
				mustRemove = False
		elif state == 'cancelled':
			mustSend = True
			nextSchedule = None # nextSchedule = time.time() + 60 * 10
		elif state == 'preSchedule':
			if not TrainUtils.isTrainStarted(train): # if not started check in 1 minute
				nextSchedule = time.time() + 60 #datetime.datetime.now() + datetime.timedelta(0, 60)
			else: mustSend = True
		else:
			# TODO manage priority and next schedule on next station
			nextSchedule =  time.time() + 60 #datetime.datetime.now() + datetime.timedelta(0, 60)
			mustSend = True

		return nextSchedule, mustSend, mustRemove;



	@classmethod
	async def sendOrEdit(self, sender, bot, chat_id, trainMsgID, text, priority):
		if priority:
			if trainMsgID == None:
				msg = await sender.sendMessage(text, disable_notification=False, parse_mode='Markdown')
			else: # instead of editing to ensure notification
				await bot.deleteMessage((chat_id, trainMsgID))
				msg = await sender.sendMessage(text, disable_notification=False, parse_mode='Markdown')
		else:
			if trainMsgID == None:
				msg = await bot.sendMessage(chat_id, text, disable_notification=False, parse_mode='Markdown')
			else:
				#print('====================')
				#print('editing msg: ' + str(chat_id) + '|' + str(trainMsgID) + '|' + text)
				try:
					msg = await bot.editMessageText((chat_id, trainMsgID), text, parse_mode='Markdown')
				except TelepotException:
					await bot.deleteMessage((chat_id, trainMsgID))
					msg = await sender.sendMessage(text, disable_notification=True, parse_mode='Markdown')
		#print(msg)
		return msg['message_id']


	@classmethod
	def isCritical(self, train):
		if 'priority' in train:
			return train['priority'] in ['critical', 'isCritical']
		return False

	@classmethod
	def getNextDayDate(self, train, trainSettings):
		if 'daysOfWeek' not in trainSettings:
			if 'executed' in trainSettings:
				return None, None
		else: daysOfWeek = trainSettings['daysOfWeek']

		if daysOfWeek == 'once':
			return None, None

		#import pdb; pdb.set_trace()
		startTime = TrainUtils.startingTimeTrain(train)

		if startTime == None: # should not happend but it happens so schedule after 5 min
			return time.time() + 5*60, None

		startTime = startTime / 1000 #startTime = self.getDateTimeFormatted(startTime)
		diff = startTime - time.time()
		todayOfWeek = datetime.datetime.today().weekday()
		if diff > 3*60: # partirà tra più di 3 minuti
			todayOfWeek += 1 # required since from settings monday is 1 instead of 0
		else: todayOfWeek += 2 # like if it is tomorrow

		daysOfWeek = list(map(int, list(daysOfWeek)))
		daysOfWeek.sort()
		if todayOfWeek <= max(daysOfWeek):
			indexNextDay = next(x[0] for x in enumerate(daysOfWeek) if x[1] >= todayOfWeek)
		else: indexNextDay = 0;

		daysMore = daysOfWeek[indexNextDay] - todayOfWeek + 1
		return startTime+daysMore*60*24*60, diff
		#return self.getDateTimeFromTimeStep(startTime+daysMore*60*24), diff
		#startTime + datetime.timedelta(daysMore, 0), diff

	@classmethod
	def isInPreSchedule(self, train):
		startTime = TrainUtils.startingTimeTrain(train)
		startTime = startTime / 1000 #startTime = self.getDateTimeFormatted(startTime)
		diff = startTime - time.time()
		return diff > 0 and diff <  self.preScheduleTime

	@classmethod
	async def getTrainStatusAndSettings(self, chat_id, trainNum, config):
		#import pdb; pdb.set_trace()
		trainSettings = config.getTrain(chat_id, trainNum)
		if trainSettings == None: # train removed
			return None, None
		#print(trainSettings)
		stationID = self.getStationID(trainSettings)
		if stationID == None: # train removed
			return None, None
		train = await TrainUtils.getTrainStatus(trainNum, stationID)
		return train, trainSettings

	@classmethod
	def getStationID(self, trainSettings):
		#import pdb; pdb.set_trace()
		if trainSettings != None and 'stationID' in trainSettings:
			return trainSettings['stationID']
		return None

	@classmethod
	def getDateTimeFormatted(self, timestamp):
		return datetime.datetime.fromtimestamp(timestamp / 1000)

	@classmethod
	def getDateTimeFromTimeStep(self, timestamp):
		return datetime.datetime.fromtimestamp(timestamp)
