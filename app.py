from flask import Flask, render_template, url_for, request, jsonify
import socket #needed to pull the hostname/ip
import os, sys
import glob
from PIL import Image
from flask_mail import Mail, Message
import config, requests, json
from flask_recaptcha import ReCaptcha
from validate_email import validate_email
import logging
from logging.handlers import RotatingFileHandler



app = Flask(__name__)
mail=Mail(app)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = config.email
app.config['MAIL_PASSWORD'] = config.password
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
app.config.update({'RECAPTCHA_ENABLED': True,
                   'RECAPTCHA_SITE_KEY':
                       config.sitekey,
                   'RECAPTCHA_SECRET_KEY':
                       config.secretkey})
recaptcha = ReCaptcha(app=app)

@app.before_request
def log_request_info():
	try:
		app.logger.info('\r\nHeaders: %s', request.headers)
		app.logger.info('Body: %s \r\n From IP: %s', request.get_data(), request.environ.get('HTTP_X_REAL_IP', request.remote_addr))
		app.logger.info('IP Addr: %s', request.environ.get('HTTP_X_REAL_IP', request.remote_addr))
	except:
		print("Erorr getting IP or other data")
    
port = '80'
hostname = socket.gethostname()
ip = socket.gethostbyname(hostname)  



if len(sys.argv) > 1:
	server_dir = str(sys.argv[1])
else:
	server_dir = os.getcwd()

print("Running from Server directory: " + server_dir)

static_dir = server_dir + '/static/eric'
static_dir_format =  "*.JPG"

def createThumbnails():
	# get all the jpg files from the static/eric folder and make thumbnails
	static_dir = server_dir + '/static/eric'
	static_dir_format =  "*.JPG"
	os.chdir(static_dir)
	print("Moved CWD to: " + os.getcwd())
	print("Looking for obsolete thumbnails")
	thb = [ fn for fn in glob.glob(static_dir_format) if os.path.basename(fn).startswith('T_')]
	for x in thb:
		if not os.path.isfile(os.getcwd() + "/" + x[2:]):
			print("Removing :" + os.getcwd() + x)
			os.remove(os.getcwd() + "/" + x)
	print("Looking for files of type: " + static_dir_format +" in : " + static_dir)
	files = [ fn for fn in glob.glob(static_dir_format) if not os.path.basename(fn).startswith('T_')]
	file_count = 0
	for infile in files:
	  if os.path.isfile(os.getcwd() + '/T_' + infile):
	  	continue
	  print("Creating Thumnail for: " + infile)
	  file_count = file_count + 1
	  im = Image.open(infile)
	  # don't save if thumbnail already exists
	  if infile[0:2] != "T_":
		# convert to thumbnail image
		im.thumbnail((512, 512), Image.ANTIALIAS)
		# prefix thumbnail file with T_
		im.save("T_" + infile, "JPEG")
	static_dir_format = "*.jpg"
	print("Looking for files of type: " + static_dir_format +" in : " + static_dir)
	files = [ fn for fn in glob.glob(static_dir_format) if not os.path.basename(fn).startswith('T_')]
	file_count = 0
	for infile in files:
	  if os.path.isfile(os.getcwd() + '/T_' + infile):
	  	continue
	  print("Creating Thumnail for: " + infile)
	  file_count = file_count + 1
	  im = Image.open(infile)
	  # don't save if thumbnail already exists
	  if infile[0:2] != "T_":
		# convert to thumbnail image
		im.thumbnail((512, 512), Image.ANTIALIAS)
		# prefix thumbnail file with T_
		im.save("T_" + infile, "JPEG")
	
	os.chdir(server_dir)
	print("Created " + str(file_count) + " Thumnails")
	print("Moved CWD to: " + os.getcwd())
	pass



createThumbnails()

@app.route('/photos')
def index(): #enumerates pictures in directory to allow listing of all
#	app.logger.info('Info')
	createThumbnails()
	images = os.listdir(static_dir)
	thumbnails = [img for img in images if img.startswith('T_')]
	thumbnails = ['eric/' + file for file in thumbnails]
	thumbnails.sort()
	return render_template('photos.html', images = thumbnails)
    #return render_template('photos.html')

@app.route('/photofolders')
def photofolders(): #enumerates pictures in directory to allow listing of all
#	app.logger.info('Info')
	createThumbnails()
	images = os.listdir(static_dir)
	thumbnails = [img for img in images if img.startswith('T_')]
	thumbnails = ['eric/' + file for file in thumbnails]
	thumbnails.sort()
	return render_template('photos.html', images = thumbnails)
    #return render_template('photos.html')

@app.route('/devices/ECB_DEV_0/messages/events',methods=['POST'])
def temp():
	app.logger.info('\r\nData: %s', request.get_json())
	return '', 204

@app.route('/confirm')
def confirm(): 
#	app.logger.info('Info')
	return render_template('confirmation.html')

@app.route('/goaway')
def goaway(): 
#	app.logger.info('Info')
	return render_template('goaway.html')

@app.route('/eric/<variable>', methods=['GET'])
def getPhoto(variable):
	#print(variable)
#	app.logger.info('Info')
	variable = variable[2:]
	variable = 'eric/' + variable
	#print(variable)
	return render_template("photo.html",image=variable)

@app.route('/', methods=['GET', 'POST'])
def landing():
#	app.logger.info('Info')
	if request.method == 'POST':
		reply_to = str(request.form.get('Email'))
		if reply_to is None:
			reply_to = "empty@empty.com"
		body = request.form.get('Message')
		name = request.form.get('Name')
		msg = Message('Contact from: ' + str(name), sender =reply_to, recipients = [config.email])
		msg.body = "From: " + str(reply_to) + "\r\n" + str(body)
		r = requests.post('https://www.google.com/recaptcha/api/siteverify',
		data = {'secret' :
			config.secretkey,
			'response' :
			request.form['g-recaptcha-response']})
		google_response = json.loads(r.text)
		print('JSON: ', google_response)
		if google_response['success']:
			print('SUCCESS')
			print(reply_to)
			if validate_email(reply_to):
				mail.send(msg)
				return render_template('confirmation.html')
		print('FAILED')
		return render_template('goaway.html')
	return render_template('landing.html')



if __name__ == '__main__':
	print("Dev Server starting on port: " + port + " at IP address: " + ip) 
	formatter = logging.Formatter("[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
	handler = RotatingFileHandler('server.log', maxBytes=10000000, backupCount=2)
	handler.setLevel(logging.DEBUG)
	handler.setFormatter(formatter)
	app.logger.addHandler(handler)
	app.logger.setLevel(logging.DEBUG)
	app.run(debug='true',host='0.0.0.0',port=port)	
	

#https://www.w3schools.com/w3css/tryit.asp?filename=tryw3css_images_album
#http://flask.pocoo.org/docs/1.0/tutorial/deploy/

#env -i /bin/bash --noprofile --norc
#https://stackoverflow.com/questions/8022530/how-to-check-for-valid-email-address