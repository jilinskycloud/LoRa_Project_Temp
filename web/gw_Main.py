
#!/usr/bin/python3
from flask import Flask
from flask import escape
from flask import url_for
from flask import request
from flask import render_template
from flask import flash
from flask import redirect
from flask import session
from flask import jsonify
from jinja2 import Template
import psutil
import time
import json
import sqlite3
import os
import redis 
import subprocess                                                                                         
r = redis.StrictRedis(host='localhost', port=6370, db=0, charset="utf-8", decode_responses=True)

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

global Xcount                                                                                   
                                                                                                
Xcount = 0 

conn = sqlite3.connect('/www/web/gw_FlaskDb.db')


def log(log_str):                                                                                                         
    global Xcount                                                                                                         
    print("in log...........:: ",Xcount)                                                                                    
    log_str = str(log_str)+" \n"                                                                                          
    Xcount = Xcount+1                                                                                                     
    with open('/tmp/flask_daemon.log', 'a') as outfile:                                                                   
        outfile.write(log_str)              
                                                                                  
    if Xcount > 10:                                                                                                      
        os.system("rm /tmp/flask_daemon.log")                                                                             
        Xcount = 0                                                                                                        
    return


#log("Opened database successfully");
conn.close()

@app.route('/getcmd', methods=['GET', 'POST'])
def getcmd():
	if request.method == 'POST':
		log("Get Command Function.......")
		input_json = request.get_json(force=True)
		os.system(input_json)
	dictToReturn = {'answer':42}
	return jsonify(dictToReturn)

@app.route('/resetLora', methods=['GET', 'POST'])
def resetLora():
	if 'username' in session:
		reset_lora = request.form['reset_lora']
		if request.method == 'POST':
			log("Switch ON/OFF BLE : "+reset_lora)
			reset_lora = request.form['reset_lora']
			#stt_ble = int(os.popen('cat /sys/class/leds/rst_lora118/brightness').read())
			#if reset_ble == 'off':
			#	os.system("echo 0 > /sys/class/leds/rst_lora118/brightness")
			#	return redirect(url_for('settings'))
			#elif reset_ble == 'on':
			#	os.system("echo 1 > /sys/class/leds/rst_lora118/brightness")
			os.system("echo 1 > /sys/class/leds/rst_ble62/brightness")
			time.sleep(2)
			os.system("echo 0 > /sys/class/leds/rst_ble62/brightness")
			return redirect(url_for('settings'))
	else:
		return redirect(url_for('login'))

@app.route('/reboot')
def reboot():
	log("System Reboot Function......")
	os.system("reboot")
	ipis = cm("ifconfig eth0| egrep -o '([[:digit:]]{1,3}\.){3}[[:digit:]]{1,3}'")
	ipis = ipis.split("\n")
	#print("--------------------------------",ipis[0])
	return "<div style='background-color:red; background-color: #e4e0e0; margin: 0px; width: 700px; text-align: center; padding: 15px; color: black; margin-left: auto; margin-right: auto;'>Device Going to Reboot! To Access Web Please <a href='http://"+ipis[0]+":5000/'>Click Here</a> After 2 minutes...</div>"

# ===================MYSQL FUNCTIONS==========================

@app.route('/delProfile/<ids>')
def delProfile(ids=None):
	conn = sqlite3.connect('/www/web/gw_FlaskDb.db')
	log("Delete Profile ID IS :: "+ids)
	f = conn.execute("DELETE FROM login where id=?", (ids,))
	conn.commit()
	conn.close()
	log("Delete Login User Function......")
	flash("Deleted successfully")
	return redirect(url_for('settings'))

#=============================================================
#=====================WEB-PAGE FUNCTIONS======================
#=============================================================

# ============================================================INDEX
@app.route('/')
@app.route('/index/')
@app.route('/index')
def index():
	if 'username' in session:
		log("Index Page Function......")
		return redirect(url_for('dashboard'))
	return redirect(url_for('login'))

# ============================================================DASHBOARD
@app.route('/dashboard')
@app.route('/dashboard/')
def dashboard():
	if 'username' in session:
		log("Dashboard Page Function......")
		u_name = escape(session['username'])
		log(session.get('device1'))
		#while(1):
		
		cmd = "hostname"                   
		proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)
		(gw_id, err1) = proc.communicate()       
		gw_id = gw_id.decode('utf-8')
		gw_id = gw_id.strip()   
		data = {}
		data['serial'] = gw_id
		data['cpu'] = psutil.cpu_percent()
		data['stats'] = psutil.cpu_stats()
		data['cpu_freq'] = psutil.cpu_freq()
		data['cpu_load'] = psutil.getloadavg()
		data['ttl_memo'] = round(psutil.virtual_memory().total/1048576)
		data['ttl_memo_used'] = round(psutil.virtual_memory().used/1048576)
		data['ttl_memo_avai'] = round(psutil.virtual_memory().available/1048576)
		data['swp_memo'] = psutil.swap_memory()
		data['hostname'] =cm("hostname")
		data['routeM'] = 'TC0981'
		data['FirmV'] = 'v3.0.11_sniffer_TainCloud_r864'
		data['lTime'] = cm('date')
		data['runTime'] = cm('uptime')
		data['network'] = cm("ifconfig eth0| egrep -o '([[:digit:]]{1,3}\.){3}[[:digit:]]{1,3}'")
		data['mount'] = psutil.disk_partitions(all=False)
		data['disk_io_count'] = psutil.disk_io_counters(perdisk=False, nowrap=True)
		data['net_io_count'] = psutil.net_io_counters(pernic=False, nowrap=True)
		data['nic_addr'] = psutil.net_if_addrs()
		data['tmp'] = psutil.sensors_temperatures(fahrenheit=False)
		data['boot_time'] = psutil.boot_time()
		data['c_user'] = psutil.users()
		data['reload'] = time.time()
		return render_template('dashboard.html', data=data)
	else:
		return redirect(url_for('login'))


def cm(dt):
	log("Inner CMD Function......Dashboard Page")
	klog = subprocess.Popen(dt, shell=True, stdout=subprocess.PIPE).stdout
	klog1 =  klog.read()
	pc = klog1.decode()
	return pc

# ============================================================Config_json

@app.route('/config_json', methods=['GET', 'POST'])
def config_json():
	if 'username' in session:
		if request.method == 'POST':
			result = request.form["json_data"]
			log(result)
			print("this is what-*******",result)
			print("this is what-*******",type(result))
			result = result.replace('\r\n', os.linesep)
			with open("/www/Lora_Pro/config.text", "w") as f:
					f.write(result)
			flash("Json File Updated")
		return redirect(url_for('settings'))
	else:
		return redirect(url_for('login'))		




# ============================================================MQTT-CONSOLE
@app.route('/console-logs')
@app.route('/console-logs/')
def mqtt_on():
    if 'username' in session:
        log("Console Logs Function......")
        klog = subprocess.Popen("dmesg", shell=True, stdout=subprocess.PIPE).stdout
        klog1 =  klog.read()
        pc = klog1.decode()
        flask = subprocess.Popen("cat /tmp/flask_daemon.log", shell=True, stdout=subprocess.PIPE).stdout
        flask =  flask.read()
        flask_log = flask.decode()
        hb = subprocess.Popen("cat /tmp/hb_daemon.log", shell=True, stdout=subprocess.PIPE).stdout
        hb =  hb.read()
        hb_log = hb.decode()
        _http = subprocess.Popen("cat /tmp/http_daemon.log", shell=True, stdout=subprocess.PIPE).stdout
        _http =  _http.read()
        _http_log = _http.decode()
        autoC = subprocess.Popen("cat /tmp/autoC_daemon.log", shell=True, stdout=subprocess.PIPE).stdout          
        autoC =  autoC.read()
        autoC_log = autoC.decode()
        return render_template('console-logs.html', data=pc, flask_log=flask_log, hb_log=hb_log, _http_log=_http_log, autoC_log=autoC_log)
    else:
        return redirect(url_for('login'))


# =============================================================BLE CONNECT

@app.route('/network', methods=['GET', 'POST'])
def network():
	if 'username' in session:
		if request.method == 'POST':
			result = request.form["net_data"]
                        ####while
			result.replace('\r','')
			log(result)
			with open("/etc/network/interfaces", "w") as f:
				#f.write(result)
				f.write(result.replace('\r\n', os.linesep))
			flash("network File Updated")
		c_dir = os.path.abspath(os.getcwd())
		#path_conf = c_dir + "/../Lora_Pro/config.text"

		net = subprocess.Popen("cat /etc/network/interfaces", shell=True, stdout=subprocess.PIPE).stdout
		net =  net.read()

                ####while

		print(net)
		net = net.decode()

		return render_template('network.html', net=net)
	else:
		return redirect(url_for('login'))		

# =============================================================Settings
@app.route('/settings/', methods=['GET', 'POST'])
def settings():
	error = None
	data = []
	rec=[]
	if 'username' in session:
		if request.method == 'POST':
			log("Setting Data Received")
			data.append(request.form['name'])
			data.append(request.form['pass'])
			log(data)
			conn = sqlite3.connect('/www/web/gw_FlaskDb.db')
			conn.execute("INSERT INTO login (username,password) VALUES (?,?)",(data[0], data[1]) )
			conn.commit()
			conn.close()
			msg = "Record successfully added"
			flash("Login Details Added successfully")
		

		conn = sqlite3.connect('/www/web/gw_FlaskDb.db')
		f = conn.execute("SELECT * FROM login")
		rec = f.fetchall()
		#print(rec)
		conn.close()
		stt_lora = os.popen('cat /sys/class/leds/rst_lora118/brightness').read()
		log("This is the BLE Reset State:: "+stt_lora)
		if int(stt_lora) == 1 or int(stt_lora) == 255:
			stt_lora = "ON"
		else:
			stt_lora = "OFF"
		#print(rec)
		autoCon123 = json.load(open('/www/web/config123.text','r'))
		print("-----------------------------------------------------------------------------------",autoCon123)

		jsonObjList = []
		c_dir = os.path.abspath(os.getcwd())
		path_conf = "/www/Lora_Pro/config.text"
		f = open(path_conf,"r")
		obj = f.read()
		'''
		with open(path_conf) as f:
			for jsonObj in f:
				jsonObj = json.loads(jsonObj)
				jsonObjList.append(jsonObj)
		'''
		return render_template('settings.html', error=error, data=data, rec=rec, chk=autoCon123, stt_lora=stt_lora, jsonObjList=obj)
	else:
		return redirect(url_for('login'))


@app.route('/connect', methods=['GET','POST'])
def connect():
	if 'username' in session:
		if request.method == 'POST':
			result = request.form.to_dict()
			print("result",result)
			with open("/www/web/config123.text", "w") as f:
				json.dump(result, f, indent=4)
				flash("Network Configuration Updated")
			print(os.system("cat /var/run/hBeat.pid"))
			pi = open("/var/run/hBeat.pid", 'r')
			pid_ = pi.read()
			pi.close()
			#print(pid_)
			os.system('kill -s 10 ' + pid_)
			pi1 = open("/var/run/pData.pid", 'r')
			pid_1 = pi1.read()
			print("this is the post pid fffff")
			print(pid_1)
			pi1.close()
			os.system('kill -s 10 ' + pid_1)
		return redirect(url_for('settings'))
	else:
		return redirect(url_for('login'))

@app.route('/update_autoCon', methods=['POST'])
def update_autoCon():
	if 'username' in session:
		if request.method == 'POST':
			log("This is the Configuration Status::"+request.form['conf_status'])
			conf_status = request.form['conf_status']
			with open('/www/web/_autoConfig/config.txt', 'r+') as f:
				data = json.load(f)
				data['auto_config'] = conf_status # <--- add `id` value.
				f.seek(0)        # <--- should reset file position to the beginning.
				json.dump(data, f, indent=4)
				f.truncate() 
		return redirect(url_for('settings'))
	else:
		return redirect(url_for('login'))

# ============================================================LOGIN PAGE
@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	#print(_mysql.initLogin_(mysql))
	if request.method == 'POST':
		u_name = request.form['username']
		u_pass = request.form['password']
		flag = 0
		conn = sqlite3.connect('/www/web/gw_FlaskDb.db')
		f = conn.execute("SELECT * FROM login WHERE username=? and password=?", (u_name, u_pass))
		#print(f)
		v = f.fetchall()
		if(len(v) > 0):
			flag = 0
		else:
			flag = -1
		#print(v)
		conn.close()
		if(flag == -1):
			error = 'Invalid Credentials. Please try again.'
		else:
			session['username'] = request.form['username']
			flash('You were successfully logged in')
			return redirect(url_for('index'))
	return render_template('login.html', error=error)

# ============================================================LOGOUT PAGE
@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('index'))


if  __name__  ==  '__main__' : 
	if os.path.exists("/tmp/flask_daemon.log") == False:                   
		print("File not exist CEATING IT")                                                   
		open("/tmp/flask_daemon.log", "w").close() 
	else:
		print("log file exists")

	while True:
		if os.path.exists("/var/run/ProcLevel.pid") == True:
			f = open("/var/run/ProcLevel.pid","r")
			pNo = f.read()
			f.close()
			if pNo == "3":
				pNo = "4"
				f= open("/var/run/ProcLevel.pid","w+")
				f.write(pNo)
				f.close()
				break
	app.run(host='0.0.0.0', port=5000)#, debug = True) #, threaded = True, ssl_context='adhoc') #Ssl_context = Context ,
