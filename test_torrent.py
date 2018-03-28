import os
import time
import subprocess
from torrentcommand import TorrentCommand



output = subprocess.Popen("deluge-console \"connect localhost:9091; info; quit\"", shell=True, stdout=subprocess.PIPE).communicate()[0]

stroutput = output.decode("utf-8")

stroutput_array = stroutput.split('\n \n')


for s in stroutput_array:
	print('-------------------------------')
	print(s)
	print('-------------------------------')

#print(output.decode("utf-8"))

#test = subprocess.Popen(["deluge-console"], stdout=subprocess.PIPE)

#TorrentCommand.is_deluge_running()

#test2 = subprocess.Popen(["connect", 'localhost:9091'], stdout=subprocess.PIPE)
#output = test.communicate()[0]

#print(test)

#os.system('deluge-console \"connect localhost:9091; \"')

#test2 = subprocess.Popen(["connect", 'localhost:9091'], stdout=subprocess.PIPE)

#time.sleep(5)

#subprocess.call("connect localhost:9091")

#os.system('connect localhost:9091')

#p = os.system('help')

#print(p)
