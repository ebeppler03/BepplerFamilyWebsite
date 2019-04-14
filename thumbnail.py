import os, sys
import glob
from PIL import Image


def createThumbnails( static_dir ):
	file_paths = []
	images = []
	file_count = 0
	for root, dirs, files in os.walk(static_dir):
		for file in files:
			file_paths.append(os.path.join(root, file))
	for file in file_paths:
		#print("file: " + file)
		if file.lower().endswith(('.png', '.jpg', '.jpeg')):
			images.append(file)
	thumbnails_files = [ fn for fn in images if os.path.basename(fn).startswith('T_')]
	for x in thumbnails_files:
		t_file_name = os.path.basename(x)
		path_name = os.path.dirname(x)
		if not os.path.isfile(path_name + "/" + t_file_name[2:]):
			print("Removing :"+ x)
			os.remove(x)
	image_files = [ fn for fn in images if not os.path.basename(fn).startswith('T_')]
	for x in image_files:
		i_file_name = os.path.basename(x)
		path_name = os.path.dirname(x)
		if os.path.isfile(path_name + '/T_' + i_file_name): #thumbnail exisits
			continue
		file_count = file_count + 1 #nneds a thumbnails
		im = Image.open(x)
		if i_file_name[0:2] != "T_":
			# convert to thumbnail image
			im.thumbnail((512, 512), Image.ANTIALIAS)
			# prefix thumbnail file with T_
			im.save(path_name + "/" + "T_" + i_file_name, "JPEG")
			print("Made for thumbnail for: " + path_name + "/" + i_file_name)
	print("Made " + str(file_count) + " thumbnails")

def createThumbnailsX():
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