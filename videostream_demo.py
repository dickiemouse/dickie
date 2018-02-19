import numpy as np
import cv2
import time

cap = cv2.VideoCapture(0)
time.sleep(2)
cap.set(3,320)
cap.set(4,240)
cap.set(cv2.CAP_PROP_FPS,10)
print("Waiting for cap open")
if not(cap.isOpened()):
    cap.open()
while (cap.isOpened()):
    # Capture frame-by-frame
##    ret = cap.set(3,240)
##    ret = cap.set(4,320)
    ret, img = cap.read()   
    # Our operations on the frame come here
    # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Display the resulting frame
    cv2.imshow('frame',img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()