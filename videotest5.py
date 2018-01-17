# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
from threading import Thread
import numpy as np

class PiVideoStream:
	def __init__(self, resolution=(640, 480), framerate=32):
		# initialize the camera and stream
		self.camera = PiCamera()
		self.camera.resolution = resolution
		self.camera.framerate = framerate
		self.rawCapture = PiRGBArray(self.camera, size=resolution)
		self.stream = self.camera.capture_continuous(self.rawCapture,
			format="bgr", use_video_port=True)

		# initialize the frame and the variable used to indicate
		# if the thread should be stopped
		self.frame = None
		self.stopped = False

	def start(self):
		# start the thread to read frames from the video stream
		Thread(target=self.update, args=()).start()
		return self

	def update(self):
		# keep looping infinitely until the thread is stopped
		for f in self.stream:
			# grab the frame from the stream and clear the stream in
			# preparation for the next frame
			self.frame = f.array
			self.rawCapture.truncate(0)

			# if the thread indicator variable is set, stop the thread
			# and resource camera resources
			if self.stopped:
				self.stream.close()
				self.rawCapture.close()
				self.camera.close()
				return

	def read(self):
		# return the frame most recently read
		return self.frame

	def stop(self):
		# indicate that the thread should be stopped
		self.stopped = True

# initialize the camera and grab a reference to the raw camera capture

#camera = PiCamera()
#camera.resolution = (640, 480)
#camera.framerate = 32
#rawCapture = PiRGBArray(camera, size=(640, 480))
 
# allow the camera to warmup

vs = PiVideoStream()
vs.start()
time.sleep(2)
 
# capture frames from the camera
while(1):
        # grab the raw NumPy array representing the image, then initialize the timestamp
        # and occupied/unoccupied text
        image = vs.read()
        cv2.imshow("raw", image)
        image1 = image
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        hsv1 = cv2.cvtColor(image1, cv2.COLOR_BGR2HSV)

        #dummy
        lower_mask = np.array([130,255,255])
        upper_mask = np.array([130,255,255])
        #green
        lower_green = np.array([65,10,10])
        upper_green = np.array([80,240,240])
        
        #red
        lower_red = np.array([0,70,50])
        upper_red = np.array([10,255,255])
        lower_red1 = np.array([170,70,50])
        upper_red1 = np.array([180,255,255])

        #mask
        mask = cv2.inRange(hsv, lower_mask, upper_mask)
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red, upper_red)
        mask3 = cv2.inRange(hsv, lower_green, upper_green)
        mask4 = mask1 + mask2

        #combine image
        res = cv2.bitwise_and(image,image, mask= mask4)
        res1 = cv2.bitwise_and(image1,image1, mask = mask3)
        combine = res + res1
        
        cv2.imwrite('test1.png',mask4)
        im = cv2.imread('test1.png')
        imgray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        ret, thresh = cv2.threshold(imgray, 127, 255, 0)
        im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        #cv2.drawContours(image, contours, -1, (0,255,0), 1)
        if len(contours)>0:
                i=0
                cnt=contours[0]
                maxarea=0
                for i in range (len(contours)):
                        mcnt = contours[i]
                        area = cv2.contourArea(mcnt)
                        if area >1500 and area>maxarea:
                                maxarea=area
                                cnt=mcnt
                try:
                        #print("area="+str(area))
                        #print ("there are " + str(len(cnt)) + " points in contours["+str(i)+"]" )
                        epsilon = 0.01*cv2.arcLength(cnt,True)     #control the percentage (0.1=10%)not acccurate
                        approx = cv2.approxPolyDP(cnt,epsilon,True)
                        #print ("after approx, there are " + str(len(approx)) + " points")
                        (x,y),radius = cv2.minEnclosingCircle(cnt)
                        center = (int(x),int(y))
                        radius = int(radius)
                        cv2.circle(image,center,radius,(0,255,0),2)
                        M = cv2.moments(cnt)
                        cx = int(M['m10']/M['m00'])
                        cy = int(M['m01']/M['m00'])
                        #print (cx)
                        #print (cy)
                        font = cv2.FONT_HERSHEY_SIMPLEX
                        #cv2.putText(img1,'ERROR!!!',(cx-50,cy+50), font, 1,(0,0,255),2)
                except:
                        print 'no red'
        
        # show the frame
        cv2.imshow("Frame", image)
        cv2.imshow("green mask", mask3)
        cv2.imshow('red mask',mask4)
        #cv2.imshow('res',res)
        #cv2.imshow('res1',res1)
        cv2.imshow('combine',combine)

        key = cv2.waitKey(1) & 0xFF
        # clear the stream in preparation for the next frame
        # if the `q` key was pressed, break from the loop
        if key == ord("q"):                
                break
        
cv2.destroyAllWindows()
vs.stop()
