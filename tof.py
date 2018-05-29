import os
import cv2
import time
import keyboard
import Tkinter as tk
from PIL import Image
from PIL import ImageTk
import threading
import numpy as np

# TODO
# http://raspberrypihq.com/how-to-turn-a-raspberry-pi-into-a-wifi-router/

# Extending the Thread class to implement some new functionalities
class TOF(threading.Thread):
	def __init__(self):
		# OpenCV
		self.font = cv2.FONT_HERSHEY_SIMPLEX
		self.prev_hist = None
		self.prev_subframe = None
		self.cap = cv2.VideoCapture(0)
		# Variables related to TIME
		self.timer_stopped = False
		self.time_flight = 0
		self.time_mat = 0
		self.time_tot = 0
		self.timer_active = False
		self.freeze_time = False

		# General variables
		self.skills = 1
		self.offset_y = 50

		# Graphics
		self.root = tk.Tk()
		self.original_panel = None
		self.tof_text = tk.Text(self.root, height = 1, width = 10)
		self.tof_text.insert(tk.END, '0')

		self.tot_text = tk.Text(self.root, height = 1, width = 10)
		self.tot_text.insert(tk.END, '0')

		self.btn_start = tk.Button(self.root, text = 'Start', width = 10, command = self.start_timer)
		self.btn_stop = tk.Button(self.root, text = 'Stop', width = 10, command = self.stop_timer)
		self.btn_stop.config(state = tk.DISABLED)
		self.btn_reset = tk.Button(self.root, text = 'Reset', width = 10, command = self.reset)
		
		self.lb_times = tk.Listbox(self.root, height = 25, width = 25)
		
		# Pack
		#	Textboxes
		self.tof_text.pack()
		self.tot_text.pack()
		#	Buttons
		self.btn_start.pack()
		self.btn_stop.pack()
		self.btn_reset.pack()
		#	Listboxes
		self.lb_times.pack(side='right')

		# Break condition
		self.break_condition = False

		# Callback when we close window
		self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)
		# This will start video
		threading.Thread.__init__(self, target = self.setup)
		return 
	def setup(self):
		# Thread for video capture
		self.videp_capture = threading.Thread(target=self.run, args=())
		self.videp_capture.start()		
		self.root.mainloop()
	def run(self):
		# First we reset the stopwatch
		self.reset()

		while not self.break_condition:
			# Capture frame-by-frame
			ret, frame = self.cap.read()
			# We are converting the image to a gray colordomain since RGB colors are not necessary
			img_original = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
			# --- IMAGE PROCESSING ---
			# Add line for threshold
			img_original = self.drawLine(img_original)

			# Text we will overlay on frame
			# 	Get change in video as float (higher value == more activity)
			change_in_video = self.change(img_original)
			# Pretty arbitrary threshold 
			if change_in_video > 0.06:
				self.timer_stopped = True

			elif change_in_video < 0.02 and self.timer_stopped:
				# If we haven't started the timer we should reset it
				if self.timer_active:
					self.time_mat += time.time() - self.start_time_mat
				else:
					self.start_time = time.time()
				
				# Save timestamp
				if self.timer_active:
					mat_time = time.time() - self.start_time_mat
					# Lastly save the time for the jump
					self.lb_times.insert(tk.END, '%d          %.2f          %.2f' % (self.skills, self.time_flight, mat_time))
					self.skills += 1
				# If last bounce stop the show
				if self.skills > 10:
					self.stop_timer()	
					# Also keep both buttons disabled until reset
					self.btn_start.configure(state = tk.DISABLED)	
				self.start_time_mat = None
				self.timer_stopped = False

			if self.timer_stopped and not self.start_time_mat:
				self.start_time_mat = time.time()
		
			if not self.timer_stopped and not self.freeze_time:
				# Get time from start
				self.time_flight = time.time() - self.start_time - self.time_mat
			if not self.freeze_time:
				self.time_tot = time.time() - self.start_time

			# Update text in boxes
			self.updateTexts()
			# Add text to frame for feedback of how much movement between frames
			img_original = self.addText(img_original, '%.2f' % change_in_video)

			# --- MAKING IMAGES FRIENDLY FOR USE in tk ---
			img_original = Image.fromarray(img_original)

			img_original = ImageTk.PhotoImage(img_original)

			# Display the resulting frames
			if self.original_panel is None:
				self.original_panel = tk.Label(image = img_original)
				self.original_panel.image = img_original
				self.original_panel.pack(side = 'left')
			else:
				self.original_panel.configure(image = img_original)
				self.original_panel.image = img_original			
	# From buttonpresses
	def start_timer(self):
		self.btn_start.configure(state = tk.DISABLED)
		self.btn_stop.configure(state = tk.NORMAL)
		self.timer_active = True
	def stop_timer(self):
		self.btn_start.configure(state = tk.NORMAL)
		self.btn_stop.configure(state = tk.DISABLED)
		self.timer_active = False
		self.freeze_time = True
	def reset(self):
		self.start_time = time.time() # Time now
		self.start_time_mat = 0
		self.time_flight = 0
		self.time_mat = 0
		self.time_tot = 0
		self.freeze_time = False
		self.skills = 1
		# Empty our listbox
		self.lb_times.delete(0, tk.END)
		# Reset buttons 
		self.btn_start.configure(state = tk.NORMAL)
		self.btn_stop.configure(state = tk.DISABLED)
		self.updateTexts()
	def updateTexts(self):
		# Reset textcontainers
		self.tof_text.delete('1.0', tk.END)
		self.tof_text.insert(tk.END, '%.2f' % self.time_flight)
		self.tot_text.delete('1.0', tk.END)
		self.tot_text.insert(tk.END, '%.2f' % self.time_tot)
	def change(self, frame):
		# Only interested in part of frame above our threshold
		cur_subframe = frame[:(self.offset_y ), :]
		if self.prev_subframe is None:
			self.prev_subframe = cur_subframe
			return 0
		euclidean_distance = np.sqrt(np.sum((cur_subframe.astype('float') - self.prev_subframe.astype('float')) ** 2))
		euclidean_distance /= cur_subframe.size
		# Set current frame as prev
		self.prev_subframe = cur_subframe
		# Return normalized sum
		return euclidean_distance
	def calcChange(self, cur_img):
		# Mask
		mask = np.ones((cur_img.size, cur_img[0].size)).astype('uint8')
		print(cur_img.size)
		print(mask.size)
		cur_hist = cv2.calcHist([cur_img.astype('float32')], 
								channels=[0], 
								mask=mask, 
								histSize=[6], 
								ranges=[0,6])

		if not self.prev_hist:
			self.prev_hist = cur_hist
			return 0
		# Calculate diff with chi-square method
		# https://docs.opencv.org/2.4/modules/imgproc/doc/histograms.html?highlight=calchist#calchist
		hist_compared_float = cv2.compareHist(prev_hist, cur_hist, method=CV_COMP_CHISQR)
		# Assign cur as prev
		self.prev_hist = cur_hist
		return hist_compared_float
	def drawLine(self, frame):
		start = (0, self.offset_y)
		end = (len(frame[0]), self.offset_y)
		return cv2.line(frame,start,end,(255,0,0),2)
	def addText(self, frame, text):
		# Returns an image with the text overlayed
		return cv2.putText(frame, text,(10,400), self.font, 4,(255,255,255),2,cv2.LINE_AA)
	def onClose(self):
		self.break_condition = True
		self.cap.release()
		self.root.quit()
	# Functions to get data from TOF class
	def getTimes(self):
		return {'flight': self.time_flight, 'total': self.time_tot}