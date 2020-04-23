import pathlib 
import subprocess
import redis
import json
import os
def readLora():
  conn = redis.StrictRedis(host='localhost', port=6370, db=0, charset="utf-8", decode_responses=True)
  c_dir = os.path.abspath(os.getcwd())
  #path_conf = c_dir + "/config.text" 
  path_conf = "/www/Lora_Pro/config.text"
  sn_ids = []
  with open(path_conf) as f:    #############################
    for jsonObj in f:
        jsonObj = json.loads(jsonObj)
        sn_ids.append(jsonObj['sensor_id'])
        #print(sn_ids)
  #print(sn_ids)

  while(1):
    #cmd = c_dir+"/receive /dev/loraSPI1.0"
    cmd = "/www/Lora_Pro/receive /dev/loraSPI1.0"
    proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)
    (sn_data, err1) = proc.communicate()
    sn_data = sn_data.decode('utf-8')
    sn_data= sn_data.split('|')
    #print("Read-Daemon ==> Rceived Sensor Data ::", sn_data)
    if sn_data[0] in sn_ids:
      #print("ID EXIST :: ", sn_data)
      temp_set = {sn_data[0]:sn_data[1]} #0 index is sensor id and index 1 is temperature
      conn.hmset("sensor_data",temp_set)


def main():
  while(1):
    readLora()


if __name__ == '__main__':
  while True:
    pNo = "1"
    f= open("/var/run/ProcLevel.pid","w+")
    f.write(pNo)
    f.close()
    main()
