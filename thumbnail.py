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