import time
import os
import redis
#os.system("rm /var/run/ProcLevel.pid")
f= open("/var/run/ProcLevel.pid","w+")
f.write("0")
f.close()
r = redis.StrictRedis(host='localhost', port=6370, db=0, charset="utf-8", decode_responses=True)
r.mset({"blink-green":"0|0|0|0|0"})
r.mset({"blink-blue":"0|0|0|0|0"})
class LedBlink:
	def blinkIt(self):
		lGreen = r.get("blink-green")
		#print(lGreen)
		x = lGreen.split("|")
		Ndelay = float(x[0])
		Nled   = x[1]
		Ntimes = int(x[2])
		Ntype  = x[3]
		Ncheck = x[4]
		if lGreen == "0|0|0|0|0":
			os.system("echo 0 > /sys/class/leds/green66/brightness")
		if Ntype == "autoConf":
			for a in range(Ntimes):
				os.system("echo 1 > /sys/class/leds/"+Nled+"/brightness")
				time.sleep(Ndelay)
				os.system("echo 0 > /sys/class/leds/"+Nled+"/brightness")
				time.sleep(Ndelay)
			r.mset({"blink-green": "0|0|0|0|0"})
		if Ntype == "heartbeat":
			os.system("echo 1 > /sys/class/leds/"+Nled+"/brightness")
			time.sleep(Ndelay)
			os.system("echo 0 > /sys/class/leds/"+Nled+"/brightness")
			time.sleep(Ndelay)
     
		lBlue  = r.get("blink-blue")
		#print(lBlue)
		x1 = lBlue.split("|")
		Ndelay1 = float(x1[0])
		Nled1   = x1[1]
		Ntimes1 = int(x1[2])
		Ntype1  = x1[3]
		Ncheck1 = x1[4]
		if Ntype1 == "scanBle":
			os.system("echo 1 > /sys/class/leds/"+Nled1+"/brightness")
			time.sleep(Ndelay1)
			os.system("echo 0 > /sys/class/leds/"+Nled1+"/brightness")
			time.sleep(Ndelay1)
			#r.mset({"blink-blue": "0|0|0|0|0"})
		elif Ntype1 == "dataPost":
			os.system("echo 1 > /sys/class/leds/"+Nled1+"/brightness")
			time.sleep(Ndelay1)
			os.system("echo 0 > /sys/class/leds/"+Nled1+"/brightness")
			time.sleep(Ndelay1)
			#r.mset({"blink-blue": "0|0|0|0|0"})
            
def main():
	obj = LedBlink()
	while True:
		obj.blinkIt()

##MAIN FUNCTION
if __name__ == '__main__':
	Ppid = "1"
	f= open("/var/run/ProcLevel.pid","w+")
	f.write(Ppid)
	f.close()
	main()