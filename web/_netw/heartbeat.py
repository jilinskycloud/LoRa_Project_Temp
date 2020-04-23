import httplib2
import json
import os
import signal
import urllib
import redis

r = redis.StrictRedis(host='localhost', port=6370, db=0, charset="utf-8", decode_responses=True)

global HB
global content
content = ""
HB = "OFF"
global start
start = 1
def status_():
	global HB
	global server_socket
	d1 = json.load(open('/www/web/config123.text','r'))
	if d1['hBeat'] == 'on':
		HB = "ON"
		print("ON")
	else:
		HB = "OFF"
		print("OFF")
	return HB

HB = status_()

def receive_signal(signum, stack):
	global HB
	HB = status_()

signal.signal(signal.SIGUSR1, receive_signal)
pidis = str(os.getpid())
print('My PID:'+pidis)
f= open("/var/run/hBeat.pid","w+")
f.write(pidis)
f.close()


def beat():
	while(1):
		global HB
		global content
		global start
		body = {'gw_id':"000001",'start':start}
		if HB == "ON":
			http = httplib2.Http(".cache",  disable_ssl_certificate_validation=True)
			url_ = "http://xy.cenwei.net:2980/api.php/admin/iot/hbMonitor"
			try:
				content = http.request(url_, method="POST", headers={'Content-type': 'application/x-www-form-urlencoded'}, body=urllib.parse.urlencode(body) )[1]
				content = content.decode("utf-8")
				#print("This is the Return :: ",content)
				start = 0
				d = json.loads(content)
				print("Heart-Beat Daemon ==> MSG::",d['msg'])
				if d['msg'] == 'reboot':
					os.system('reboot')
				elif d['msg'] == 'config':
					print("This is the DATA",d['data'])
					cont = d['data']
					start = 3
					print("CONT DATA::",type(cont))
					
					with open('/www/web/rec_config.text', 'a') as outfile:
						outfile.write(json.dumps(d['data']))
						outfile.write("\n")
						outfile.close()

					#with open("/www/web/rec_config.text", 'w') as outfile:
					#	json.dump(d['data'], outfile) 
					start = 3
			except Exception as e:
				pass 
		elif HB == 'OFF':
			pass

def main():
	while(1):
		beat()


##MAIN FUNCTION
if __name__ == '__main__':
  while True:    
    if os.path.exists("/var/run/ProcLevel.pid") == True:
      f = open("/var/run/ProcLevel.pid","r")                                                    
      pNo = f.read()
      f.close() 
      if pNo == "1":
        pNo = "2"
        f= open("/var/run/ProcLevel.pid","w+")
        f.write(pNo)                                                      
        f.close()                         
        main()   
