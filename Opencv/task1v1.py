
# import the necessary packages
import time
import cv2
import numpy as np

# initialize the camera and grab a reference to the raw camera capture

#camera = PiCamera()
#camera.resolution = (640, 480)
#camera.framerate = 32
#rawCapture = PiRGBArray(camera, size=(640, 480))

# allow the camera to warmup

# vs = PiVideoStream()
# vs.start()
# time.sleep(2)

# capture frames from the camera
# while(1):
        # grab the raw NumPy array representing the image, then initialize the timestamp
        # and occupied/unoccupied text
        # image = vs.read()
image = cv2.imread('main_replastering.jpg')

cv2.imshow("raw", image)
image1 = image
hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
hsv1 = cv2.cvtColor(image1, cv2.COLOR_BGR2HSV)

#dummy
lower_mask = np.array([130,255,255])
upper_mask = np.array([130,255,255])
#green
lower_green = np.array([65,10,10])
upper_green = np.array([80,255,255])

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
mask5 = mask4 + mask3

#combine image
res = cv2.bitwise_and(image,image, mask= mask1)
res1 = cv2.bitwise_and(image1,image1, mask = mask3)
combine = res + res1

cv2.imwrite('test1.png',mask4)
im = cv2.imread('test1.png')
cv2.imwrite('test2.png',mask3)
im7 = cv2.imread('test2.png')

imgray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
imgray1 = cv2.cvtColor(im7, cv2.COLOR_BGR2GRAY)

ret, thresh = cv2.threshold(imgray, 127, 255, 0)
ret8, thresh8 = cv2.threshold(imgray1, 127, 255, 0)

im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
im8, contours8, hierarchy8 = cv2.findContours(thresh8, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
cx=0
cy=0
cx1=0
cy1=0
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
                #print (cx,cy)

                font = cv2.FONT_HERSHEY_SIMPLEX
                #cv2.putText(img1,'ERROR!!!',(cx-50,cy+50), font, 1,(0,0,255),2)
        except:
                print ('no red')

if len(contours8)>0:
        i=0
        cnt=contours8[0]
        maxarea=0
        for i in range (len(contours8)):
                mcnt = contours8[i]
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
                cv2.circle(image,center,radius,(0,0,255),2)
                M = cv2.moments(cnt)
                cx1 = int(M['m10']/M['m00'])
                cy1 = int(M['m01']/M['m00'])
                #print (cx,cy)
                font = cv2.FONT_HERSHEY_SIMPLEX
                #cv2.putText(img1,'ERROR!!!',(cx-50,cy+50), font, 1,(0,0,255),2)
        except:
                print ('no green')
#print("red",cx,cy)
#print("green",cx1,cy1)
cxm= (cx+cx1)/2
cym= (cy+cy1)/2
#print ('midpoint', cxm,cym)

# show the frame
cv2.imshow("Frame", image)
cv2.imshow("green mask", mask3)
#cv2.imshow('red mask',mask4)
#cv2.imshow('res',res)
#cv2.imshow('res1',res1)
#cv2.imshow('combine',mask5)

key = cv2.waitKey(0)
# clear the stream in preparation for the next frame
# if the `q` key was pressed, break from the loop

cv2.destroyAllWindows()
# vs.stop()
