# Developed by Upstream
# Last Modify: 14 april 2017
# For MATE PC-Pi Connection
# Client(PC) Side

from GUI.GUI import *
from Module.xinput import *
import math
import serial
import serial.tools.list_ports
import struct
import asyncore, socket
import threading
import time
import random, os, sys

MAX_RECV = 4096 # Maximum Data Receive Length
# Server Information
Server_host = '192.168.1.2'
#Server_host = 'localhost'
Server_port = 8080

def controller_setup(probe_frequency):
    joysticks = None

    print('%d controller found' % len(joysticks))

    j = joysticks[0]
    j.probe_frequency = probe_frequency
    j.ftMode = 0
    j.ftDirectMode = 0
    j.pid = True
    j.piMode = 0
    j.motorX = 0
    j.motorY = 0
    j.rotateX = 0
    j.rotateY = 0
    j.sendFloat = False
    j.sendPitch = False
    j.decrementLow = 0
    j.decrementHigh = 0
    j.pitch = 0
    j.head = 0
    j.sendPID = False
    j.waitData = False
    j.waitResetP = False
    j.curMode = 0
    j.depthS = False
    j.pitchS = False
    j.yawS = False
##    j.dtz = False
    j.calDepth = False
    print('Using controller %d' % j.device_number)
   
    @j.event
    def on_button(button, pressed):
        buttonStr = ''
        if button == 13:
            if pressed == 1:
               #buttonStr = 'A'
               j.ftDirectMode = 1
               j.sendFloat = True
        elif button == 16:
            ### issue command to cal depth
            if pressed == 1:
               #buttonStr = 'Y'
               j.calDepth = True
##               if not j.pid:
##                  gui.setMeter(0)
##               else:
##                  j.dtz = True 
##               j.sendFloat = True
            elif pressed == 0:
               j.calDepth = False
        elif button == 14:
            if pressed == 1:
               #buttonStr = 'B'
               j.ftDirectMode = -1
               j.sendFloat = True
        elif button == 15:
            #buttonStr = 'X'
            #read data(maybe)
            if pressed == 1:
               j.waitData = True
               j.sendPID = True
        #elif button == 7:
            #buttonStr = 'LS'
        #elif button == 8:
            #buttonStr = 'RS'
        elif button == 6:
            #buttonStr = 'Back'
            if pressed == 0:
               j.piMode = 0
               j.sendPitch = True
               j.waitResetP = False
            else:
               if j.waitResetP:
                  j.piMode = -2
                  j.waitResetP = False
               else:
                  if j.pitch > -180:
                     j.piMode = -1
                  j.waitResetP = True
        elif button == 5:
            #buttonStr = 'Start'
            if pressed == 0:
               j.piMode = 0
               j.sendPitch = True
               j.waitResetP = False
            else:
               if j.waitResetP:
                  j.piMode = -2
                  j.waitResetP = False
               else:
                  if j.pitch < 180:
                     j.piMode = 1
                  j.waitResetP = True
        elif button == 9:
            #buttonStr = 'LB'
            if pressed == 0:
               j.decrementLow = 0
            else:
               j.decrementLow = 1   
        elif button == 10:
            #buttonStr = 'RB'
            if pressed == 0:
               j.ftMode = 0
               j.sendFloat = True
            elif j.pid:
               j.ftMode = 1
        elif button == 1:
            if pressed == 1:
               #buttonStr = 'Up'
               j.curMode += 1
               if j.curMode == 4:
                  j.curMode = 0
        elif button == 2:
            if pressed == 1:
               #buttonStr = 'Down'
               j.yawS = not j.yawS
        elif button == 3:
            if pressed == 1: 
               #buttonStr = 'Left'
               j.depthS = not j.depthS
        elif button == 4:
            if pressed == 1:
               #buttonStr = 'Right'
               j.pitchS = not j.pitchS
               gui.ps()
        #else:
            #buttonStr = str(button) 
        #if buttonStr != '':
           #print('button', buttonStr, pressed)

    @j.event
    def on_axis(axis, value):
        if axis == 'right_trigger':
           #print('RT')
           if value == 0 and j.ftMode == -1:
              j.ftMode = 0
              j.sendFloat = True
           else:
              if value >= 0.25 and j.pid:
                 j.ftMode = -1
              elif value >= 0.25 :
                 j.ftMode = -1
        elif axis == 'left_trigger':
           #print('LT')
           if value == 0:
              j.decrementHigh = 0
           elif value >= 0.75:
              j.decrementHigh = 1
        elif axis == 'l_thumb_y':
           if value >= 0.1 or value <= -0.11:
              j.motorY = value
           else:
              j.motorY = 0
           #print('axis', axis, value)
        elif axis == 'l_thumb_x':
           if value >= 0.08 or value <= -0.08:
           #if value >= 0.03 or value <= -0.03:
              j.motorX = value
           else:
              j.motorX = 0
           #print('axis', axis, value)
        elif axis == 'r_thumb_y':
           if value >= 0.1 or value <= -0.1:
              j.rotateY = value
           else:
              j.rotateY = 0
           #print('axis', axis, value)
        elif axis == 'r_thumb_x':
           if value >= 0.1 or value <= -0.1:
              j.rotateX = value
           else:
              j.rotateX = 0
           #print('axis', axis, value)
        #else:
         #  print('axis', axis, value)

    return j

def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)

def calPower(x,y):
    p = round(math.sqrt(x*x+y*y)/0.5*100)
    if p > 100:
       p = 100
    if x == 0:
       if y > 0:
          return p,0
       else:
          return p,180
    elif y == 0:
       if x > 0:
          return p,90
       else:
          return p,270
    a = math.degrees(math.atan(abs(x)/abs(y)))
    #print(a)
    if x >= 0:
       if y >= 0:
          pass
       else:
          a = 180-a
    else:
       if y >= 0:
          a = 360-a
       else:
          a += 180
    return p,a

def rotatePt(x,y,mode):
   if mode == 0:
      return x,y
   elif mode == 1:
      return y,-x
   elif mode == 2:
      return -x,-y
   elif mode == 3:
      return -y,x

def reconnect(portName):
   ser = None
   while 1:
      try:
         ser = serial.Serial(portName,baudrate=115200)
         break
      except serial.serialutil.SerialException:
         pass
   return ser
   
if __name__ == "__main__":
   # init varible
   camList = [0,0,0,0,0,0,0,0]
   armList = [0,0,0,0,0,0,0]
   valveList = [0,0]
   preCam = []
   preArm = []
   preValve = []
   preMotorA = -181
   preRotateA = -181
   preMotorP = -1
   preDepth = -1
   preRoll = -181
   prePitch = -181
   preHead = -181
   sendDepth = 0
   curDepth = 0
   curYaw = 0
   curRoll = 0
   curPitch = 0
   curTemp = 0
   calDepthTimer = -1
   depthScaleL = 100
   depthScaleS = 2
   depthLimit = 1500
   floatMode = 0
   dMode = -1
   yMode = -1
   pMode = -1
   floatingScale = 0.5 #for 100% power
   enableReset = False
   yawUpdate = True
   yawUpdateCheck = False
   initPID = True
   pidCurBool = [False,False,False]
   initCounter = 50
   gui.setState(-1)
   gui.update()
   j = controller_setup(2000,gui)
   gui.setState(1)
   gui.update()
   gui.setState(-2)
   gui.update()
   curTime = int(round(time.time()*1000))
   serialPort = serial.Serial(port=portName,baudrate=115200)
   gui.setState(1)
   gui.update()
   tempFineFloat = 0
   while 1:
      packet = []
##      packet = bytearray()

      if initPID:
         if initCounter > 0:
            initCounter -= 1
         else:
            initPID = False
            packet.append(0xF4)
            print("Req")

      #controller
      try:
         j.dispatch_events()
      except RuntimeError:
         print('Controller disconnected.\nReconnecting...')
         gui.setState(-1)
         gui.update()
         j = controller_setup(2000,gui)
         gui.setState(1)
         gui.update()

      #floating
      #mode 1: old version with power
      #use when pid fail
      if not j.pid:
         if j.ftMode != 0:
            if j.ftMode == 1:
               tempFineFloat = gui.getMeter()
               if tempFineFloat == 99 or tempFineFloat == -1:
                  j.ftMode = 0
               gui.setMeter(tempFineFloat+1)
            elif j.ftMode == -1:
               tempFineFloat = gui.getMeter()
               if tempFineFloat == -99 or tempFineFloat == 1:
                  j.ftMode = 0
               gui.setMeter(tempFineFloat-1)            
            #print(j.ftMode)
         
      #mode 0: direct change depth
      #for pid
      else:
         #depth
         if preDepth == -1:
            preDepth = 0
            sendDepth = 0
         tempDepth = preDepth
         if j.ftMode != 0:
            if j.ftMode == -1:
               if tempDepth + depthScaleS > depthLimit:
                  tempDepth = depthLimit
                  j.ftMode = 0
               else:
                  tempDepth += depthScaleS
            else:
               if tempDepth - depthScaleS < -700:
                  tempDepth = -700
                  j.ftMode = 0
               else:
                  tempDepth -= depthScaleS
         if j.ftDirectMode == 1:
            if tempDepth + depthScaleL > depthLimit:
               tempDepth = depthLimit
            else:
               tempDepth += depthScaleL
            j.ftDirectMode = 0
         elif j.ftDirectMode == -1:
            if tempDepth - depthScaleL < -700:
               tempDepth = -700
            else:
               tempDepth -= depthScaleL
            j.ftDirectMode = 0
##         if j.dtz:
##            tempDepth = 0
##            j.dtz = False
         preDepth = tempDepth
         if tempDepth == sendDepth:
            j.sendFloat = False
         gui.setText(2,[preDepth,curDepth])
         if j.sendFloat:
            sendDepth = preDepth
            packet.append(0xA1)
            tempShort = struct.pack('h',sendDepth)
            for i in tempShort:
               packet.append(int(i))
            j.sendFloat = False
            
            packet+=bytearray([0xA1])
            packet+=struct.pack('h',preDepth)
         if (gui.getMeter() != 0):
            change = floatingScale * gui.getMeter() / 100
            if (preDepth - change) <= 0:
               tempDepth = 0
            else:
               tempDepth = preDepth - change
            if preDepth != tempDepth:
               preDepth = tempDepth
               gui.setText(2,int(preDepth))
               packet+=bytearray([0xA1])
               packet+=struct.pack('h',int(preDepth))

      if dMode == -1:
         packet.append(0xAB)
         packet.append(0x00)
         dMode = False
      elif dMode != j.depthS:
         dMode = j.depthS
         packet.append(0xAB)
         if dMode:
            packet.append(0x01)
         else:
            packet.append(0x00)

      if yMode == -1:
         packet.append(0xB7)
         packet.append(0x00)
         yMode = False
      elif yMode != j.yawS:
         yMode = j.yawS
         packet.append(0xB7)
         if yMode:
            packet.append(0x01)
         else:
            packet.append(0x00)
            
      if pMode == -1:
         packet.append(0xAD)
         packet.append(0x00)
         pMode = False
      elif pMode != j.pitchS:
         pMode = j.pitchS
         packet.append(0xAD)
         if pMode:
            packet.append(0x01)
         else:
            packet.append(0x00)
            
      #roll
      if preRoll == -181:
         preRoll = 0
         packet.append(0xA5)
         packet.append(0x80)

      #pitch
      if prePitch == -181:
         prePitch = 0
         packet.append(0xA3)
         packet.append(0x80)
      if j.piMode == -2:
         j.pitch = 0
         j.piMode = 0
         gui.setPitch(j.pitch)
      elif j.piMode != 0:
         if j.piMode == -1:
            if j.pitch == -180:
               j.piMode = 0
            else:
               j.pitch -= 1
               if j.pitch == 0:
                  j.piMode = 0
         else:
            if j.pitch == 180:
               j.piMode = 0
            else:
               j.pitch += 1
               if j.pitch == 0:
                  j.piMode = 0
         gui.setPitch(round(j.pitch))
      if j.sendPitch:
         tempPitch = 0
         #map
         if j.pitch == 0:
            tempPitch = 0x80
         elif j.pitch > 0:
            tempPitch = round(translate(j.pitch,1,180,129,255))
         else:
            tempPitch = round(translate(j.pitch,-180,-1,0,127))
         print(tempPitch)
         #send
         packet.append(0xA3)
         packet.append(tempPitch)
         j.sendPitch = False

      #thruster
      if j.motorX != 0 or j.motorY != 0:
         enableReset = True
         p,a=calPower(j.motorX,j.motorY)
         #print(p)
         a = int(a)
         tempP = 0
         if p >= 100:
            if j.decrementLow == 0 and j.decrementHigh == 0:
               tempP = 40
            elif j.decrementHigh == 1 and j.decrementLow == 1:
               tempP = 200
            elif j.decrementHigh == 1:
               tempP = 120
            else:
               tempP = 80
         gui.setMotor(tempP,a)
         a += gui.getDirection()*90
         if a > 360:
            a -= 360
         if a >= 181:
            tempA = -(360-a)
         else:
            tempA = a
         #print('T:',tempA)
         if (preMotorA == -181 or preMotorP == -1) or (preMotorA != tempA or preMotorP != tempP):
            preMotorA = tempA
            preMotorP = tempP
            packet+=bytearray([0xB1])
            packet+=struct.pack('h',int(preMotorA))
            packet+=bytearray([preMotorP])
            packet.append(0xB1)
            tempShort = struct.pack('h',int(preMotorA))
            #print(int(preMotorA))
            #print(tempShort[0],tempShort[1],struct.unpack('h',tempShort))
            for i in tempShort:
               packet.append(int(i))
            packet.append(tempP)
            
      else:
         if enableReset:
            if preMotorA != 0 or preMotorP != 0:
               gui.resetMotor()
               preMotorA = 0
               preMotorP = 0
               packet+=bytearray([0xB1])
               packet+=struct.pack('h',int(preMotorA))
               packet+=bytearray([preMotorP])
               packet.append(0xB1)
               tempShort = struct.pack('h',int(preMotorA))
               for i in tempShort:
                  packet.append(int(i))
               packet.append(preMotorP)
               enableReset = False
            
      #yaw
      if preHead == -181:
         preHead = 0
         tempHead = preHead
         gui.setHead(preHead)
         #send
         packet.append(0xB3)
         tempShort = struct.pack('h',int(preHead))
         for i in tempShort:
            packet.append(int(i))
      if j.rotateX != 0 or j.rotateY != 0:
         p,a=calPower(j.rotateX,j.rotateY)
         if p>=75 and j.rotateY < 0.3 and j.rotateY > -0.3:
            if j.rotateX < 0:
               tempHead -= 3
            else:
               tempHead += 3
            if tempHead > 180:
            #if tempHead > 360:
               tempHead -= 360
            if tempHead < -180:
            #if tempHead < 0:
               tempHead += 360
            gui.setHead(tempHead)
            yawUpdate = False
      else:
         if preHead != tempHead:
            preHead = tempHead
            if preHead >= 181:
               tempA = -(360-preHead)
            else:
               tempA = preHead
            #print(tempA)
            #send
            packet.append(0xB3)
            tempShort = struct.pack('h',int(tempA))
            for i in tempShort:
               packet.append(int(i))
            yawUpdate = True
            yawUpdateCheck = False

      if j.sendPID:
         getPID = True
         j.sendPID = False
         data = gui.getInput()
         t = 0
         for arr in data:
            if set(arr) != {''}:
               getPID = False
               if t == 0:
                  packet.append(0xA7)
               elif t == 1:
                  packet.append(0xA9)
               elif t == 2:
                  packet.append(0xB5)
               for i in arr:
                  if i == '':
                     tempFloat = 0
                  else:
                     tempFloat = float(i)
                  #print(tempFloat)
                  tempFloat = struct.pack('f',tempFloat)
                  for n in tempFloat:
                     packet.append(int(n))
            t += 1
         if getPID:
            getPID = False
            packet.append(0xF4)
            print("F4")
            
      if j.calDepth:
         if calDepthTimer == -1:
            calDepthTimer = int(round(time.time()*1000))
         curDepthTimer = int(round(time.time()*1000))
         if (curDepthTimer - calDepthTimer) >= 2000:
            j.calDepth = False
            packet.append(0xAC)
            print("cal depth")
      if not j.calDepth and calDepthTimer != -1:
         calDepthTimer = -1
         #print("reset")
         
      #Check if cur pid is well received
      if pidCurBool[0] and pidCurBool[1] and pidCurBool[2]:
         packet.append(0xF6)
         pidCurBool = [False,False,False]
      
      #control panel
      try:
         if serialPort.inWaiting() >= 4:
            tempType = serialPort.read(1)
            if tempType[0] == 0xC1:
               tempArray = serialPort.read(8)
               preCam = list(tempArray)
               packet.append(0xC1)
               for i in preCam:
                  packet.append(int(i))
               gui.setText(0,preCam)
            elif tempType[0] == 0xD1:
               tempArray = serialPort.read(2)
               packet.append(0xD1)
               for i in tempArray:
                  packet.append(int(i))
            elif tempType[0] == 0xD2:
               tempArray = serialPort.read(7)
               packet.append(0xD2)
               for i in tempArray:
                  packet.append(int(i))


      except serial.serialutil.SerialException:
         serialPort = reconnect(portName)
         #packet+=tempArray         
   
      #print(len(packet))
      #if len(packet) != 0:
         #print(packet)
      #if(server.client_thread.client.Connect):
      #server.write(packet)
                  
      #Send data to server
      tempStr = ''
      for i in packet:
         tempStr += chr(i)
      server.write(tempStr)

      # read data from server      
      tempTime = int(round(time.time()*1000))
      if (tempTime - curTime) >= 200:
         readData = server.read()
         if readData:
            dataList = []
            for i in readData:
               dataList.append(ord(i))
            data = bytearray(dataList)
            i = 0
            while i < len(data):
               #print(data[i])
               if data[i] == 0xE1:
			   """
                  tempData = data[i+1:i+5]
                  i += 5
                  #print("TD",tempData)
                  tempTemp = struct.unpack('f',bytearray(tempData))[0]
                  #print(tempTemp)
                  if tempTemp != curTemp:
                     curTemp = tempTemp
                     gui.setText(1,'{:.2f}'.format(curTemp))
			    """
                  tempData = data[i+1:i+8]
                  i += 8
                  tempTemp = ''
                  for tempi in tempData:
                     tempTemp += str(tempi, encoding = "utf-8")
                  #print(tempTemp)
                  if tempTemp != curTemp:
                     curTemp = tempTemp
                     gui.setText(1,tempTemp)
               elif data[i] == 0xE2:
                  tempData1 = data[i+1:i+3]
                  tempData2 = data[i+3:i+5]
                  i += 5
                  tempPitch = int(struct.unpack('h',bytearray(tempData1))[0])
                  tempRoll = int(struct.unpack('h',bytearray(tempData2))[0])
                  #print(tempPitch)
                  if tempPitch != curPitch:
                     curPitch = tempPitch
                     gui.setCurPitch(curPitch)
                  if tempRoll != curRoll:
                     curRoll = tempRoll
                     gui.setRoll(curRoll)
               elif data[i] == 0xE4:
                  tempData = data[i+1:i+3]
                  i += 3
                  tempYaw = int(struct.unpack('h',bytearray(tempData))[0])
                  if tempYaw != curYaw:
                     curYaw = tempYaw
                     gui.setCurHead(curYaw)
               elif data[i] == 0xE6:
                  tempData = data[i+1:i+3]
                  i += 3
                  tempDepth = int(struct.unpack('h',bytearray(tempData))[0])
                  if tempDepth != curDepth:
                     curDepth = tempDepth
                     gui.setText(2,[preDepth,curDepth])
               elif data[i] == 0xE7:
                  tempData = data[i+1:i+3]
                  i+=3
                  tempYawSetPoint = int(struct.unpack('h',bytearray(tempData))[0])
                  #print(tempYawSetPoint,preHead)
                  if(preHead != tempYawSetPoint and yawUpdate):
                     if(yawUpdateCheck):
                        tempHead = tempYawSetPoint
                        preHead = tempHead
                        gui.setHead(tempHead)
                     yawUpdateCheck = True
               elif data[i] == 0xF5:
                  tempPCur = data[i+1:i+5]
                  i += 5
                  tempICur = data[i:i+4]
                  i += 4
                  tempDCur = data[i:i+4]
                  i += 4                 
                  #print("TD",tempData)
                  #print("Yaw")
                  tempP = struct.unpack('f',bytearray(tempPCur))[0]
                  #print(tempP)
                  tempI = struct.unpack('f',bytearray(tempICur))[0]
                  #print(tempI)
                  tempD = struct.unpack('f',bytearray(tempDCur))[0]
                  #print(tempD)
                  #!!!!!!!!!!!!!!! Map to GUI (Yaw)
                  gui.setCurText([tempP,tempI,tempD],2)
                  pidCurBool[0] = True
               elif data[i] == 0xF7:
                  tempPCur = data[i+1:i+5]
                  i += 5
                  tempICur = data[i:i+4]
                  i += 4
                  tempDCur = data[i:i+4]
                  i += 4                 
                  #print("TD",tempData)
                  #print("Depth")
                  tempP = struct.unpack('f',bytearray(tempPCur))[0]
                  #print(tempP)
                  tempI = struct.unpack('f',bytearray(tempICur))[0]
                  #print(tempI)
                  tempD = struct.unpack('f',bytearray(tempDCur))[0]
                  #print(tempD)
                  #!!!!!!!!!!!!!!!! Map to GUI (Depth)
                  gui.setCurText([tempP,tempI,tempD],0)
                  pidCurBool[1] = True
               elif data[i] == 0xF9:
                  tempPCur = data[i+1:i+5]
                  i += 5
                  tempICur = data[i:i+4]
                  i += 4
                  tempDCur = data[i:i+4]
                  i += 4                 
                  #print("TD",tempData)
                  #print("Pitch")
                  tempP = struct.unpack('f',bytearray(tempPCur))[0]
                  #print(tempP)
                  tempI = struct.unpack('f',bytearray(tempICur))[0]
                  #print(tempI)
                  tempD = struct.unpack('f',bytearray(tempDCur))[0]
                  #print(tempD)
                  #!!!!!!!!!!!!!!!! Map to GUI (Pitch)
                  gui.setCurText([tempP,tempI,tempD],1)
                  pidCurBool[2] = True

         curTime = tempTime  
      gui.update()

      
      #for i in packet:
         #print(i)
##      if j.waitData:
##         data = server.read()
##         server.write("Received")
##         if (data):
##            print(int(data))
##            j.waitData = False
      #gui.refresh()
      #print(server.read())
      #print("send Data:", server.write(str(random.randrange(100))))
      #time.sleep(2)
      
