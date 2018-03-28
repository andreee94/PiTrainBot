import sys
import datetime
from TrainMonitor.TrainMonitor import viaggiatreno

class TrainUtils:

	@classmethod
	def format_timestamp(self, ts, fmt='%H:%M:%S'):
		if self.is_valid_timestamp(ts):
			return datetime.datetime.fromtimestamp(ts/1000).strftime(fmt)
		else:
			return 'N/A'

	@classmethod
	def is_valid_timestamp(self, ts):
		return (ts is not None) and (ts > 0) and (ts < 2147483648000)


	@classmethod
	def getDaysOfWeekFormatted(self, daysOfWeek):
		if daysOfWeek == 'once':
			return 'Once'
		days = ['M', 'T', 'W', 'T', 'F', 'S', 'S']

		if self.isstring(daysOfWeek):
			daysOfWeek = list(map(int, list(daysOfWeek)))

		#import pdb; pdb.set_trace()
		text = ''
		for i in range(1, 7+1):
			if i in daysOfWeek:
				text += days[i-1]
			else: text += '-'
			text += ' '
		return text.strip()

	@classmethod
	def column(self, matrix, i):
		return [row[i] for row in matrix]

	@classmethod
	async def existsAndUnique(self, trainNum):
		# return exists, isunique, stationName, stationID
		api = viaggiatreno.API()
		departures = api.call('cercaNumeroTrenoTrenoAutocomplete', trainNum)
		#import pdb; pdb.set_trace()
		if len(departures) == 0:
			return False, False, None, None
		elif len(departures) == 1:
			return True, True, departures[0][0], departures[0][1]
		else:
			return True, False, self.column(departures, 0),  self.column(departures, 1)

	@classmethod
	async def getTrainStatus(self, trainNum, stationID):
		api = viaggiatreno.API()
		train_status = api.call('andamentoTreno', stationID, trainNum)
		#import pdb; pdb.set_trace()
		return train_status

	@classmethod
	def isTrainCancelled(self, train_status):
		return train_status['tipoTreno'] == 'ST' or train_status['provvedimento'] == 1

	@classmethod
	def isTrainStarted(self, train_status):
		return train_status['stazioneUltimoRilevamento'] != None

	@classmethod
	def isTrainArrived(self, train_status):
		return train_status['stazioneUltimoRilevamento'] == train_status['destinazione']

	@classmethod
	def startingTimeTrain(self, train_status):
		#import pdb; pdb.set_trace()
		print(train_status)
		if train_status == None or 'fermate' not in train_status:
			return None
		f = train_status['fermate']
		if f != None and len(f) > 0 and 'partenza_teorica' in f[0]:
			return f[0]['partenza_teorica']
		return None

	@classmethod
	def bold(self, text):
		return '*' + text + '*'

	@classmethod
	def nextStation(self, train_status):
		if self.isTrainArrived(train_status):
			return None
		for f in train_status['fermate']:
			partenzaReale = f['partenzaReale']
			if partenzaReale == None:
				return f
		return None

	@classmethod
	def currentStation(self, train_status):
		if self.isTrainArrived(train_status):
			return None
		if not self.isTrainStarted(train_status):
			return None
		oldf = None
		for f in train_status['fermate']:
			partenzaReale = f['partenzaReale']
			if partenzaReale == None:
				return oldf
			oldf = f
		return None


	@classmethod
	def printAllStations(self, train_status):
		text = '' # 'Train number: '
		for f in train_status['fermate']:
			text += '--> ' + self.bold(f['stazione'])
			text += '\n'

			isFirstStation = f['tipoFermata'] == 'P'
			isLastStation = f['tipoFermata'] == 'A'

			arrivoReale = f['arrivoReale']
			partenzaReale = f['partenzaReale']
			ritardoPartenza = f['ritardoPartenza']
			ritardoArrivo = f['ritardoArrivo']

			arrivoProgrammato = f['arrivo_teorico']
			partenzaProgrammata = f['partenza_teorica']
			binarioArrivoProgrammato = f['binarioProgrammatoArrivoDescrizione']
			binarioPartenzaProgrammato = f['binarioProgrammatoPartenzaDescrizione']
			if not isFirstStation:
				if arrivoReale != None:
					text += 'arrived at ' + self.format_timestamp(arrivoReale, fmt='%H:%M')
					text += ' | delay --> *' + str(ritardoArrivo) + ' min*'
					text += '\n'
				elif arrivoProgrammato != None:
					text += 'expected arrival at ' + self.format_timestamp(arrivoProgrammato, fmt='%H:%M')
					text += ' |  binary ' + str(binarioArrivoProgrammato)
					text += '\n'
			if not isLastStation:
				if partenzaReale != None:
					text += 'started at ' + self.format_timestamp(partenzaReale, fmt='%H:%M')
					text += ' | delay --> *' + str(ritardoPartenza) + ' min*'
					text += '\n'
				elif partenzaProgrammata != None:
					text += 'expected departure at ' + self.format_timestamp(arrivoProgrammato, fmt='%H:%M')
					text += ' | binary ' + str(binarioPartenzaProgrammato)
					text += '\n'

		return text.strip()

	@classmethod
	def printTrainCancelled(self, train_status):
		trainNum = train_status['numeroTreno']
		text = 'Train ' + str(trainNum)
		if 'fermate' in train_status:
			if len(train_status['fermate']) > 0:
				f = train_status['fermate'][0]
				stazionePartenza = f['stazione']
				orarioPartenza = self.format_timestamp(f['partenza_teorica'], fmt='%H:%M')
				text += ' from ' + stazionePartenza # + '\n'
				text += ' at ' + orarioPartenza

		text += ' is *CANCELLED*'
		return text

	@classmethod
	def printTrainArrived(self, train_status):
		trainNum = train_status['numeroTreno']
		f = train_status['fermate'][-1]
		stazioneArrivo = f['stazione']
		ritardo = f['ritardoArrivo']
		orarioArrivo = self.format_timestamp(f['arrivoReale'], fmt='%H:%M')
		text = 'Train ' + str(trainNum) + ' is *ARRIVED* at ' + stazioneArrivo
		text += ' at ' + orarioArrivo +  ' with delay of *' + str(ritardo) + ' min*'
		text += '\n'
		text += self.printAllStations(train_status)
		return text


	@classmethod
	def isstring(self, s):
		import sys
		# if we use Python 3
		if (sys.version_info[0] >= 3):
			return isinstance(s, str)
		# we use Python 2
		return isinstance(s, basestring)
