import os
import httplib2
import urllib
import time
import subprocess
import redis
import json
global content
global conn
global HB
import signal

content = ""
conn  = redis.StrictRedis(host='localhost', port=6370, db=0, charset="utf-8", decode_responses=True)



HB = "OFF"

def status_():
  global HB
  global server_socket
  d1 = json.load(open('/www/web/config123.text','r'))
  if d1['pData'] == 'on':
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
f= open("/var/run/pData.pid","w+")
f.write(pidis)
f.close()






def get_from_redis(sn_id):
  global conn
  if conn.hexists("sensor_data",sn_id) == 1:
    return conn.hget("sensor_data",sn_id)
  else:
    #print(sn_id, "-ID doesn't Exists!!!!")
    return "NULL"

def set_last_send_time_from_redis(sn_id):
  global conn
  last_send = {sn_id:time.time()} #0 index is sensor id and index 1 is temperature
  conn.hmset("last_send_time",last_send)
  #print("Set Last Send time")
  return 0

def get_last_send_time_from_redis(sn_id):
  global conn
  if conn.hexists("last_send_time",sn_id) == 1:
    #print("get Last Send time")
    return conn.hget("last_send_time",sn_id)
  else:
    last_send = {sn_id:0} 
    conn.hmset("last_send_time",last_send)
    return conn.hget("last_send_time",sn_id)

def Post_LoRa_Data():
  global conn
  jsonObjList = []
  c_dir = os.path.abspath(os.getcwd())
  #path_conf = c_dir + "/config.text"
  path_conf = "/www/Lora_Pro/config.text"
  #conn.del("sensor_data")

  all_keys = list(conn.hgetall('sensor_data').keys())
  conn.hdel('sensor_data', *all_keys)

  with open(path_conf) as f:
    for jsonObj in f:
      jsonObj = json.loads(jsonObj)
      jsonObjList.append(jsonObj)
  
  
  while(1):
    #print("in while LOOP-------")
    for SN in jsonObjList:
      
      #print(SN["server_url"], SN["post_url"], SN["sensor_id"], SN["time_to_send"], SN["protocol_type"], SN["service_type"])
      temp = get_from_redis(SN["sensor_id"])
      last_time = get_last_send_time_from_redis(SN["sensor_id"])  ####################
      s_t  = SN["service_type"]
      url_ = SN["server_url"]+SN["post_url"]
      sn_id = SN["sensor_id"]

      cmd = "hostname"
      proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)
      (gw_id, err1) = proc.communicate()
      gw_id = gw_id.decode('utf-8')
      gw_id = gw_id.strip()
      #print("this is ", gw_id)
      #gw_id = '0001'
      #print("This is the GW ID ::",gw_id)
      #print("C_time -- 001",float(time.time()))
      #print("L_time -- 001",float(last_time))
      #print("L_time -- 001",float(SN["time_to_send"]))
      #time.sleep(2)
      #xt = time.time() - float(last_time)
      #vt = float(SN["time_to_send"])
      #print("--001---  ",xt ," > ", vt)
      if HB == "ON":
        if float(time.time()) - float(last_time) > float(SN["time_to_send"]):
          #print("check 001")
          #print("--002--- This is the temp", temp)
          if temp != "NULL": 
            print("pData is ON")
            #print("--003-- This is the TEMP From Redis::",temp)
            s = '{\"s_time\":\"'+time.ctime()+'\", \"gw_id\":\"'+gw_id+'\", \"sn_id\":\"'+sn_id+'\", \"ST\":\"'+s_t+'\", \"temp\":\"'+temp[:6]+'\"}' 
            print("Sent Packet",s)
            global content 
            body = {'post_data':s}
            http = httplib2.Http(".cache",  disable_ssl_certificate_validation=True)
            url_ = "http://xy.cenwei.net:2980/api.php/admin/iot/saveMonitor"
            try:
              #print("check-----004")
              content = http.request(url_, method="POST", headers={'Content-type': 'application/x-www-form-urlencoded'}, body=urllib.parse.urlencode(body) )[1]
              content = content.decode("utf-8")
              last_send = time.ctime()
              print("Post-Daemon ==> This is server MSG", content)
              #print("Sent")
              set_last_send_time_from_redis(SN["sensor_id"])  ################
            except Exception as e:
              #print(e)
              pass 
        else:
          tmp = 0         
          #print("check 002")
      else:
        print("pData is OFF")
        pass



def main():
  while True:
    Post_LoRa_Data()

if __name__ == '__main__':
	
  while True:
    if os.path.exists("/var/run/ProcLevel.pid") == True:
      f = open("/var/run/ProcLevel.pid","r")
      pNo = f.read()
      f.close()
      if pNo == "2":
        pNo = "3"
        f = open("/var/run/ProcLevel.pid","w+")
        f.write(pNo)
        f.close()
        main()
