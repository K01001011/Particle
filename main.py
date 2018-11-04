from __future__ import print_function
from PIL import Image
from PIL import ImageTk
import tkinter as tki
import threading
import datetime
import imutils
import cv2
import os
import subprocess
from recognize_faces import face_rec
from train_encode import trainer
from face_datasets import dataset
from get_pulse import getPulseApp
import argparse
import errno
import time
import pyrebase

config = {
    "apiKey": "API_KEY",
    "authDomain": "DOMAIN",
    "databaseURL": "URL",
    "storageBucket": "STORAGE_URL"
}

firebase = pyrebase.initialize_app(config)

db = firebase.database()
sb = firebase.storage()

class PhotoBoothApp:
	def __init__(self, vs, outputPath):
                # store the video stream object and output path, then initialize
		# the most recently read frame, thread for reading frames, and
		# the thread stop event
                self.vs = vs
                self.outputPath = outputPath
                self.frame = None
                self.thread = None
                self.stopEvent = None

		# initialize the root window and image panel
                self.root = tki.Tk()
                self.panel = None
		
                self.w = self.root.winfo_screenwidth()
                self.h = self.root.winfo_screenheight()
		
                self.frame1 = tki.Frame(self.root, width = 250, height = self.h, bg = 'white')
                self.frame1.grid(row = 0, column = 1, sticky = "nsew")
		
                self.button1 = tki.Button(self.frame1, width = 27, text = "Measure heart rate", command = self.get_plse).grid(row = 0, column = 1, sticky = 'we')
		
                self.photo = tki.PhotoImage(file = 'two.jpg')
                self.v = tki.StringVar()
                self.space = tki.Label(self.frame1, width = 27, height = 1, bg = 'white').grid(row = 1, column = 1)
                self.label = tki.Label(self.frame1, width = 27, text = "To-Do").grid(row = 2, column = 1, sticky = 'we')
                self.space1 = tki.Label(self.frame1, width = 27, height = 1, bg = 'white').grid(row = 3, column = 1)
                self.label1 = tki.Label(self.frame1, width = 27, image = self.photo).grid(row = 4, column = 1, sticky = 'we')
                self.space1 = tki.Label(self.frame1, width = 27, height = 1, bg = 'white').grid(row = 5, column = 1)
                self.mtextbox = tki.Entry(self.frame1, textvariable=self.v).grid(row = 6, column = 1)
                self.button2 = tki.Button(self.frame1, width = 27, text = "Upload Datasets", command = self.upload).grid(row = 7, column = 1, sticky = 'we')
                self.space1 = tki.Label(self.frame1, width = 27, height = 1, bg = 'white').grid(row = 8, column = 1)
                self.button2 = tki.Button(self.frame1, width = 27, text = "Train", command = self.train_bro).grid(row = 9, column = 1, sticky = 'we')
                self.space1 = tki.Label(self.frame1, width = 27, height = 1, bg = 'white').grid(row = 10, column = 1)
                self.button2 = tki.Button(self.frame1, width = 27, text = "face recognition", command = self.face_recs).grid(row = 11, column = 1, sticky = 'we')
# create a button, that when pressed, will take the current
		# frame and save it to file
		#btn = tki.Button(self.root, text="Snapshot!",
		#	command=self.takeSnapshot)
		#btn.pack(side="bottom", fill="both", expand="yes", padx=10,
		#	pady=10)

		# start a thread that constantly pools the video sensor for
		# the most recently read frame
                self.stopEvent = threading.Event()
                self.thread = threading.Thread(target=self.videoLoop, args=())
                self.thread.start()

		# set a callback to handle when the window is closed
                self.root.wm_title("Particle")
                self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)
	def videoLoop(self):
		# DISCLAIMER:
		# I'm not a GUI developer, nor do I even pretend to be. This
		# try/except statement is a pretty ugly hack to get around
		# a RunTime error that Tkinter throws due to threading
		try:
			# keep looping over frames until we are instructed to stop
			while not self.stopEvent.is_set():
				# grab the frame from the video stream and resize it to
				# have a maximum width of 300 pixels
				self.frame = self.vs.read()
				#self.frame = imutils.translate(self.frame, 0, 0)
				self.frame = imutils.resize(self.frame, width = 650)

				# OpenCV represents images in BGR order; however PIL
				# represents images in RGB order, so we need to swap
				# the channels, then convert to PIL and ImageTk format
				image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
				image = Image.fromarray(image)
				image = ImageTk.PhotoImage(image)
		
				# if the panel is not None, we need to initialize it
				if self.panel is None:
					self.panel = tki.Label(width = self.w-250, height = self.h, image=image)
					self.panel.image = image
					self.panel.grid(row = 0, column = 0)
					#self.panel.pack(side="left", padx=10, pady=10)
		
				# otherwise, simply update the panel
				else:
					self.panel.configure(image=image)
					self.panel.image = image

		except RuntimeError as e:
			print("[INFO] caught a RuntimeError")
	def onClose(self):
		# set the stop event, cleanup the camera, and allow the rest of
		# the quit process to continue
		print("[INFO] closing...")
		self.stopEvent.set()
		self.vs.stop()
		self.root.quit()
	def train_bro(self):
                trainer()
	def upload(self):
                input = self.v.get()
                print(input)
                try:
                    os.makedirs("alphaParticle/dataset/" + input)
                except OSError as e:
                    if e.errno != errno.EEXIST:
                        raise
                dataset(self.vs, "alphaParticle/dataset/" + input)
	def get_plse(self):
                parser = argparse.ArgumentParser(description='Webcam pulse detector.')
                parser.add_argument('--serial', default=None,
                        help='serial port destination for bpm data')
                parser.add_argument('--baud', default=None,
                        help='Baud rate for serial transmission')
                parser.add_argument('--udp', default=None,
                        help='udp address:port destination for bpm data')
                
                self.vs.stop()
                args = parser.parse_args()
                getPulseApp(args)
                
	def face_recs(self):
                names = face_rec(self.vs).returnNames()
                print(names)
                dataValue = db.child(names).child("todo").order_by_child("listData").get()
                cur = "To-Do\n"
                for value in dataValue.each():
                    vasl = db.child(names).child("todo").child(value.key()).child("listData").get()
                    print(vasl.val())
                    cur += vasl.val() + "\n"
                    time.sleep(1)
                    #ur = self.label.cget() + vasl.val()
                labs = tki.Label(self.frame1, text = cur).grid(row = 2, column = 1, sticky = 'we')
                
                sb.child(names).child("six.jpg").download("download.jpg")
                
                img = Image.open('download.jpg')
                img = img.resize((250, 250),Image.ANTIALIAS)
                img.save("dwnld.ppm", "ppm")
                img = tki.PhotoImage(file = 'dwnld.ppm')
                #img = img.zoom(25)
                labsa = tki.Label(self.frame1, width = 27, image = img).grid(row = 4, column = 1, sticky = 'we')
                labsa.photo = img
                #wait=input("Press enter to continue")
                #shellscript = subprocess.Popen(['/home/pi/Particle/face_rec.sh'], stdin = subprocess.PIPE)
                #shellscript.check_output()