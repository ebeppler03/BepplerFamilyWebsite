from flask import Flask, render_template, url_for
import socket #needed to pull the hostname/ip
import os, sys
import glob
from PIL import Image


app = Flask(__name__)


port = '8080'
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
	os.chdir(server_dir)
	print("Created " + str(file_count) + " Thumnails")
	print("Moved CWD to: " + os.getcwd())
	pass



createThumbnails()

@app.route('/photos')
def index(): #enumerates pictures in directory to allow listing of all
	createThumbnails()
	images = os.listdir(static_dir)
	thumbnails = [img for img in images if img.startswith('T_')]
	thumbnails = ['eric/' + file for file in thumbnails]
	thumbnails.sort()
	return render_template('photos.html', images = thumbnails)
    #return render_template('photos.html')

@app.route('/eric/<variable>', methods=['GET'])
def getPhoto(variable):
	#print(variable)
	variable = variable[2:]
	variable = 'eric/' + variable
	#print(variable)
	return render_template("photo.html",image=variable)

@app.route('/', methods=['GET', 'POST'])
def landing():
    return render_template('landing.html')

if __name__ == '__main__':
	print("Dev Server starting on port: " + port + " at IP address: " + ip) 
	app.run(debug='true',host='0.0.0.0',port=port)	
	

#https://www.w3schools.com/w3css/tryit.asp?filename=tryw3css_images_album
#http://flask.pocoo.org/docs/1.0/tutorial/deploy/

#env -i /bin/bash --noprofile --norc