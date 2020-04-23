import os
import subprocess
import time


def check_http():
  proc = subprocess.Popen(["ps ax | grep 'python3 /www/web/_netw/_httplib.py' | grep -v grep | awk '{print $1}'"], stdout=subprocess.PIPE, shell=True)
  (pid, err) = proc.communicate()
  pid = str(pid,'utf-8')
  #print("Process PID is ::", pid)
  #cmd = "kill -9 " + str(pid)
  if pid == "" :
    print("it's null")
    pNo = "5"
    f= open("/var/run/ProcLevel.pid","w+")
    f.write(pNo)       
    f.close()
    os.system("/etc/init.d/http_daemon start")
  else:
    print("Process is running with PID ::", pid)
    #os.system(cmd)
    #subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)
    #print("This is the process ID of heartbeat", pid)



def check_hb():
  proc = subprocess.Popen(["ps ax | grep 'python3 /www/web/_netw/heartbeat.py' | grep -v grep | awk '{print $1}'"], stdout=subprocess.PIPE, shell=True)
  (pid, err) = proc.communicate()
  pid = str(pid,'utf-8')
  #print("Process PID is ::", pid)
  #cmd = "kill -9 " + str(pid)
  if pid == "" :
    pNo = "4"
    f= open("/var/run/ProcLevel.pid","w+")
    f.write(pNo)       
    f.close()
    os.system("/etc/init.d/hb_daemon start")
  else:
    print("Process is running with PID ::", pid)
    #os.system(cmd)
    #subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)
    #print("This is the process ID of heartbeat", pid)


def check_flask():                                                 
  proc = subprocess.Popen(["ps ax | grep 'python3 /www/web/gw_Main.py' | grep -v grep | awk '{print $1}'"], stdout=subprocess.PIPE, shell=True)
  (pid, err) = proc.communicate()                                                                                                                
  pid = str(pid,'utf-8')                                                                                                                         
  #print("Process PID is ::", pid)                                                                                                                
  #cmd = "kill -9 " + str(pid)                                                                                                                   
  if pid == "" :                                                                                                                                 
    print("it's null") 
    pNo = "3"
    f= open("/var/run/ProcLevel.pid","w+")
    f.write(pNo)       
    f.close()  
    os.system("/etc/init.d/flask_daemon start")                                                                                                                        
  else:                                                                                                                                          
    print("Process is running with PID ::", pid)
    #os.system(cmd)                             
    #subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)
    #print("This is the process ID of heartbeat", pid) 






while(True):
  time.sleep(2)
  check_hb()
  check_http()
  check_flask()
  print("----------------------------------------------------")
