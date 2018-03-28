
import sys
import datetime
from TrainMonitor.TrainMonitor import viaggiatreno
from trainutils import TrainUtils

def format_timestamp(ts, fmt='%H:%M:%S'):
    if is_valid_timestamp(ts):
        return datetime.datetime.fromtimestamp(ts/1000).strftime(fmt)
    else:
        return 'N/A'


def is_valid_timestamp(ts):
    return (ts is not None) and (ts > 0) and (ts < 2147483648000)

api = viaggiatreno.API()



departures = api.call('cercaNumeroTrenoTrenoAutocomplete', 4918)
departure_ID = departures[0][1]
train_status = api.call('andamentoTreno', departure_ID, 4918)
print(departures)
#print(train_status)

print ('Last tracking in {0} at {1}'.format(
            train_status['stazioneUltimoRilevamento'],
            format_timestamp(train_status['oraUltimoRilevamento'])
        ))

for f in train_status['fermate']:
    print('{} | {} | {} | {}'.format(f['stazione'], f['tipoFermata'], format_timestamp(f['partenzaReale']), format_timestamp(f['arrivoReale'])))

	# if f['tipoFermata'] == 'P':
	# 	actual = format_timestamp(f['partenzaReale'])
	# else: actual = format_timestamp(f['arrivoReale'])
    #
	# print(actual)

departures = api.call('cercaNumeroTrenoTrenoAutocomplete', 88)
print(departures)
print('lenght of departures = ' + str(len(departures)))


departures = api.call('cercaNumeroTrenoTrenoAutocomplete', 2621)
departure_ID = departures[0][1]
train_status = api.call('andamentoTreno', departure_ID, 2621)
print(TrainUtils.printAllStations(train_status))
