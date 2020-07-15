from flask import Flask,render_template
from scipy.spatial import distance as dist
from imutils.video import VideoStream
from imutils import face_utils
from threading import Thread
import numpy as np
import playsound
import argparse
import imutils
import time
import dlib
import cv2
import os

app = Flask(__name__)
app.secret_key = os.urandom(12)
def sound_alarm(path):
	playsound.playsound(path)
def eye_aspect_ratio(eye):
	A = dist.euclidean(eye[1], eye[5])
	B = dist.euclidean(eye[2], eye[4])
	C = dist.euclidean(eye[0], eye[3])
	ear = (A + B) / (2.0 * C)
	return ear
@app.route('/')
def home():
	return render_template("index.html")
@app.route('/start', methods=['GET','POST'])
def start():
    EYE_AR_THRESH = 0.25
    max=0.3
    EYE_AR_CONSEC_FRAMES = 30
    COUNTER = 0
    ALARM_ON = False
    print("[INFO] loading facial landmark predictor...")
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')
    (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
    (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
    print("[INFO] starting video stream thread...")
    vs = VideoStream(0).start()
    time.sleep(1.0)
    while True:
    	frame = vs.read()
    	frame = imutils.resize(frame, width=450)
    	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    	rects = detector(gray, 0)
    	for rect in rects:
    		shape = predictor(gray, rect)
    		shape = face_utils.shape_to_np(shape)
    		leftEye = shape[lStart:lEnd]
    		rightEye = shape[rStart:rEnd]
    		leftEAR = eye_aspect_ratio(leftEye)
    		rightEAR = eye_aspect_ratio(rightEye)
    		ear = (leftEAR + rightEAR) / 2.0
    		if ear > max:
    			max=ear
    			EYE_AR_THRESH = max*0.75
    			print(EYE_AR_THRESH)
    		leftEyeHull = cv2.convexHull(leftEye)
    		rightEyeHull = cv2.convexHull(rightEye)
    		cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
    		cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)
    		if ear < EYE_AR_THRESH:
    			COUNTER += 1
    			if COUNTER >= EYE_AR_CONSEC_FRAMES:
    				if not ALARM_ON:
    					ALARM_ON = True
    					if ('alarm.wav') != "":
    						t = Thread(target=sound_alarm('alarm.wav'),
    							args=('alarm.wav'))
    						t.deamon = True
    						t.start()
    				cv2.putText(frame, "DROWSINESS ALERT!", (10, 30),
    					cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    		else:
    			COUNTER = 0
    			ALARM_ON = False
    		cv2.putText(frame, "EAR: {:.2f}".format(ear), (300, 30),
              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    	cv2.imshow("Frame", frame)
    	key = cv2.waitKey(1) & 0xFF
    	if key == ord("q"):
    		break
    cv2.destroyAllWindows()
    vs.stop()
    return render_template("1.html")  
if __name__ == "__main__":
    app.run()
    
