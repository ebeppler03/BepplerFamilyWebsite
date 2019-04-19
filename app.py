from flask import Flask, render_template, url_for, request, jsonify
import socket #needed to pull the hostname/ip
import os, sys
import glob
from PIL import Image
from flask_mail import Mail, Message
import config, requests, json
import thumbnail
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

#setup all the logging
@app.before_request
def log_request_info():
	try:
		app.logger.info('\r\nHeaders: %s', request.headers)
		app.logger.info('Body: %s \r\n From IP: %s', request.get_data(), request.environ.get('HTTP_X_REAL_IP', request.remote_addr))
		app.logger.info('IP Addr: %s', request.environ.get('HTTP_X_REAL_IP', request.remote_addr))
	except:
		print("Erorr getting IP or other data")

#configure the connections and ports
#if this is dev use 8080, otherwise use 80    
port = '80'
hostname = socket.gethostname()
ip = socket.gethostbyname(hostname)  


#get the server directory and setup the static directory
if len(sys.argv) > 1:
	server_dir = str(sys.argv[1])
else:
	server_dir = os.getcwd()
static_dir = server_dir + '/static/photos'
print("Running from Server directory: " + server_dir)
print("static dir: " + static_dir)
photo_dir = server_dir + '/static/photos'
static_dir = server_dir + '/static'

thumbnail.createThumbnails(static_dir) #make thumbnails now to save load time

# @app.route('/photos')
# def index(): #enumerates pictures in directory to allow listing of all
# #	app.logger.info('Info')
# 	thumbnails = []
# 	#photo_dir = server_dir + '/static/photos'
# 	#os.chdir(static_dir)
# 	#print("Moved CWD to: " + os.getcwd())
# 	thumbnail.createThumbnails(photo_dir)
# 	#static_dir = server_dir + '/static'
# 	#images = os.listdir(static_dir)
# 	for root, dirs, files in os.walk(static_dir):
# 		for file in files:
# 			rel_dir = os.path.relpath(root, static_dir)
# 			if os.path.basename(file).startswith('T_'):
# 				thumbnails.append(os.path.join(rel_dir, file))
# 	thumbnails.sort()
# 	os.chdir(server_dir)
# 	#eric fix the template path!
# 	return render_template('photos.html', images = thumbnails)
#     #return render_template('photos.html')

@app.route('/photos')
@app.route('/photos/')
@app.route('/photofolders')
@app.route('/photofolders/')
def photofolders(): #enumerates pictures in directory to allow listing of all
	unsafe_directory = request.args.get('dir',default = None, type = str)
	if unsafe_directory is not None:
		directory = unsafe_directory.replace('..','')
	else:
		directory = None
	print directory
	thumbnails = []
	pic_folders = []
	thumbnail.createThumbnails(photo_dir)
	#photo_dir = server_dir + '/static/photos'
	if directory is None:
		directory = server_dir + '/static/photos'
	elif directory == "photos":
		directory = server_dir + '/static/photos'
	else:
		directory = server_dir + '/static/photos/' + directory
	if not os.path.isdir(directory):
		directory = server_dir + '/static/photos'
	files = os.listdir(directory)
	for f in files:
		if os.path.basename(f).startswith('T_'):
			rel_dir = os.path.relpath(directory, static_dir)	
			thumbnails.append(os.path.join(rel_dir, f))
	for root, dirs, files in os.walk(directory):
		for direc in dirs:
			rel_dir = os.path.relpath(root, photo_dir)
			pic_folders.append(os.path.join(rel_dir,direc))
		#pull out pics and folders here
	#check if dir exists in current path, save path, check for sub dirs, if none show pics, if load with modded path
	return render_template('photos.html', folders = pic_folders, images = thumbnails)

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

@app.route('/photo/')
@app.route('/photo')
def getPhoto():
	#print(variable)
#	app.logger.info('Info')
	thumbnail = request.args.get('pic',default = None, type = str)
	full_photo = thumbnail.replace('T_','')
	#create path to photo from static
	# variable = variable[2:]
	# variable = 'photos/' + variable
	#print(variable)
	return render_template("photo.html",image=full_photo)

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
	app.run(debug='true',host='0.0.0.0',port=port,threaded=True)	
	

#https://www.w3schools.com/w3css/tryit.asp?filename=tryw3css_images_album
#http://flask.pocoo.org/docs/1.0/tutorial/deploy/

#env -i /bin/bash --noprofile --norc
#https://stackoverflow.com/questions/8022530/how-to-check-for-valid-email-address