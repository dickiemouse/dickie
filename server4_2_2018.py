# Developed by Upstream
# Last Modify: 17 January 2018
# For AUV Pi-arduino connection
# Server(Pi) Side

import struct
import serial
import asyncore, socket
import threading
import time
import os
import random, sys
import controlApi as ctl

MAX_RECV = 4096 # Maximum Data Receive Length
# Server Information
Server_host = '192.168.1.2'
Server_port = 8080

# for serial mapping
serialMap = [serial.Serial(),serial.Serial(),serial.Serial(),serial.Serial()]
serialStatus = [False,False,False,False]
serialName = ['','','','']


# motor variable
motorValue = [False,False]
motor = [0,0,0,0,0,0]

#depth, yaw, (pitch, roll) variable
a1Bool = [False,False,False]
depth = 0
yaw = 0
pitch = 0
row = 0

# return corresponding serial number
def serialNumber(detail):
   if detail == 0xA1:
      return 0
   elif detail == 0xB1:
      return 1
   elif detail == 0xC1:
      return 2
   elif detail == 0xD1:
      return 3
   return -1

# reconnect serial port
def serialReconnect(portName):
   ser = None
   while 1:
      try:
         ser = serial.Serial(portName,115200)
         break
      except serial.serialutil.SerialException:
         print("Serial unable to reconnect.")
         time.sleep(5)
         pass
   return ser

# disable the duplicate port when reconnecting
def serialDisable(sNum,portName):
   if(sNum == -1): return
   for i in range(4):
      if(i != sNum and serialName[i] == serialName[sNum]):
         serialStatus[i] = False
         serialMap[i] = None #have to check if serial.Serial() or None is better
         serialName[i] = portName

def send(forward):
    writeTo = -1
    try:
       if(forward[0] in ctl.sendToArduino0):
          writeTo = 0
          serialMap[0].write(bytes(forward))     
       elif(forward[0] in ctl.sendToArduino1):
          writeTo = 1
          serialMap[1].write(bytes(forward))
    except serial.serialutil.SerialException:
       if (writeTo != -1):
           print("Serial ",writeTo," Port:",serialName[writeTo]," is disconnected")
           serialStatus[writeTo] = False
           serialTemp = serialReconnect(serialName[writeTo])
           serialTemp.write(command)

def receive(forward):
    # Serial Read loop
    received = False
    if(forward[0] in ctl.sendToArduino0):
                    receivedFrom = 0     
    elif(forward[0] in ctl.sendToArduino1):
        receivedFrom = 1
    while not (received):
        serialTemp = serialMap[receivedFrom] # Temp for current Arduino
        try:
           otherPort = -1
           otherPortName = ''
           if(serialTemp.inWaiting() >= 2):
              info = serialTemp.read(1)
              if info[0] == 0xF2:
                 detail = serialTemp.read(1)
                 sNum = serialNumber(detail[0])
                 if(sNum == -1):
                    print("Connected Arduino does not match the system / Return Data Error, data:",detail[0])
                 else:
                    serialMap[sNum] = serialTemp
                    # if different from orignal port, record and erase another one by serialDisable Function
                    if(serialName[sNum] != serialMap[sNum].port):
                       otherPort = sNum
                       otherPortName = serialName[sNum]
                    serialName[sNum] = serialMap[sNum].port
                    if(not serialStatus[sNum]):
                       print("Serial No:",sNum+1," Port:",serialMap[sNum].port,"is online")
                    serialStatus[sNum] = True
              elif info[0] == 0xE3: # Arduino 1
                 motor[0] = struct.unpack('h',serialTemp.read(2))
                 motor[1] = struct.unpack('h',serialTemp.read(2))
                 motorValue[0] = True
                 print('Motor 0:',motor[0],'Motor 1:', motor[1])
                 received = True
              elif info[0] == 0xE4: # Arduino 2
                 yaw = struct.unpack('h',serialTemp.read(2))
                 a1Bool[1] = True
                 print('Yaw is:',yaw)
                 received = True
              elif info[0] == 0xE5: # Arduino 2
                 motor[2] = struct.unpack('h',serialTemp.read(2))
                 motor[3] = struct.unpack('h',serialTemp.read(2))
                 motor[4] = struct.unpack('h',serialTemp.read(2))
                 motor[5] = struct.unpack('h',serialTemp.read(2))
                 motorValue[1] = True
                 print('Motor 2:',motor[2],'Motor 3:',motor[3],'Motor 4:',motor[4],'Motor 5:',motor[5])
                 received = True
              elif info[0] == 0xE6: # Arduino 1
                 depth = struct.unpack('h',serialTemp.read(2))
                 print('depth:',depth)
                 a1Bool[0] = True
                 received = True
              elif info[0] == 0xE7: # Arduino 1
                 yawSetPoint = struct.unpack('h',serialTemp.read(2))
                 print('Yaw Value:',yawSetPoint)
                 received = True
        except serial.serialutil.SerialException:
            print("Serial Error Occur, Port: ",writeTo)
            serialTemp = serialReconnect(serialName[writeTo])
            serialTemp.write(command)
    serialDisable(otherPort,otherPortName)
    if((serialTemp.inWaiting() >= 2) and received):
        serialTemp.read(serialTemp.inWaiting())
    elif((serialTemp.inWaiting() <= 2) and not received):
        send(forward)
       
      # check serial status
    
if __name__ == "__main__":
   # write strace shell file
   traceFile = open("trace.sh","w")
   temp = 'strace -f -e write -p'+str(os.getpid())+' 2>&1 | grep --color "\\".*\\""'
   traceFile.write(temp)
   traceFile.close()

   #----------------------------Serial Port Setup
   # init serial variable
   serialNo = [serial.Serial(),serial.Serial(),serial.Serial(),serial.Serial()]

   # init serial port
   command = bytearray([0xF1]) # command for get arduino type
   serialNo[0] = serialReconnect('/dev/ttyUSB0')
   serialNo[1] = serialReconnect('/dev/ttyUSB1')
   serialNo[2] = serialReconnect('/dev/ttyUSB2')
   # serialNo[3] = serialReconnect('/dev/ttyUSB3')
   # write command for serial mapping
##   serialNo[0].write(command)
##   serialNo[1].write(command)
##   serialNo[2].write(command)
##   serialNo[3].write(command)

   # serial mapping before main loop
   while 1:
      # for serial mapping
      serialNo[0].write(command)
      serialNo[1].write(command)
      serialNo[2].write(command)
      # serialNo[3].write(command)
      for i in range(3):
         try:
##            if(serialMapped[i]):
##               continue
##            else serialNo[i].write(command)
            print(i,':',serialNo[i].inWaiting())
            if(serialNo[i].inWaiting() >= 2):
               info = serialNo[i].read(1)
               if info[0] == 0xF2:
                  detail = serialNo[i].read(1)
                  sNum = serialNumber(detail[0])
                  if(sNum == -1):
                     print("Connected Arduino does not match the system / Return Data Error, data:",detail[0])
                  else:
                     serialMap[sNum] = serialNo[i]
                     if(not serialStatus[sNum]):
                        print("Serial No:",sNum+1," Port:",serialMap[sNum].port,"is online")
                     serialStatus[sNum] = True
##                     serialMapped[i] = True
                     serialName[sNum] = serialMap[sNum].port
               elif info[0] == 0xE1: # if go up data on Arduino3 appear first
                  detail = serialNo[i].read(7)
                  info += detail
                  serialMap[2] = serialNo[i]
                  if(not serialStatus[2]):
                     print("Serial No: 3 Port:",serialMap[2].port,"is online")
                  serialStatus[2] = True
##                  serialMapped[i] = True
                  serialName[2] = serialMap[2].port
                  # try to write to client      
         except serial.serialutil.SerialException:
            print("Serial Error Occur, Port: ",i)
            name = '/dev/ttyUSB'+str(i)
            serialNo[i] = serialReconnect(name)
      print(serialStatus[0],serialStatus[1],serialStatus[2],serialStatus[3])
      time.sleep(2)
      #if(serialStatus[0] and serialStatus[1] and serialStatus[2] and serialStatus[3]):
      if(serialStatus[0] and serialStatus[1]):
         print('All Arduino is ready')
##      #---For Debugging---
##      print(serialStatus[1])
##      time.sleep(3)
##      if(serialStatus[1] and serialStatus[0]):
         break
##   print(serialMap)
##   print(serialName)
            
      
   #--------------------------------Main loop
   serialTemp = serial.Serial() # temp varible for reconnection
   curTime = int(round(time.time()*1000))
   depthPID = []
   yawPID = []
   pitchPID = []
   dbool = False
   ybool = False
   pbool = False
   sendPID = FalseserialTemp = serial.Serial() # temp varible for reconnection
   curTime = int(round(time.time()*1000))
   
   while 1:
      # Timer for request PID return
##      tempTime = int(round(time.time()*1000))
##      if (tempTime - curTime) >= 500:
##         serialMap[0].write(bytearray([0xFA,0xFB,0xFE]))
##         serialMap[1].write(bytearray([0xFC,0xFD,0xFF]))
##         curTime = tempTime
      # check serial status
      ##path
      send(ctl.getDepth())
      receive(ctl.getDepth())
      time.sleep(5)
      send(ctl.getThruster2())
      receive(ctl.getThruster2())
      time.sleep(5)
      send(ctl.getThruster4())
      receive(ctl.getThruster4())
      time.sleep(5)
      send(ctl.getYaw())
      receive(ctl.getYaw())
      time.sleep(5)
      send(ctl.getYawValue())
      receive(ctl.getYawValue())
      time.sleep(5)
