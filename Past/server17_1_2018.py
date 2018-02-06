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

# Handle Client Connection
##class AgentServer(asyncore.dispatcher):
##   def __init__(self, port):
##      asyncore.dispatcher.__init__(self)
##      # client socket
##      self.clientSocket = None
##      # Server Setup
##      self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
##      self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
##      self.bind((Server_host, Server_port))
##      self.listen(1) # listen to 1 client only
##
##   def handle_accept(self):
##      if(self.clientSocket):
##         self.clientSocket.handle_close()
##      # Accept Socket
##      self.clientSocket, address = self.accept()
##      print ('New client from : ' + address[0])
##      # Socket Handler Setup
##      self.clientSocket = ClientAgent(self.clientSocket)
##
### Socket Handler
##class ClientAgent(asyncore.dispatcher):
##   def __init__(self, socket):
##      asyncore.dispatcher.__init__(self, socket)
##      self.SendData = ""
##      self.RecvData = ""
##      self.counter = 0 # data transmission failure counter
##      self.Connect = True
##
##   # receive data from client
##   def handle_read(self):
##      temp = self.recv(MAX_RECV)
##      if len(temp) > 0:
##         self.RecvData = temp
##
##   # Getter for received data
##   def data_recv(self):
##      if len(self.RecvData) > 0:
##         temp = self.RecvData
##         self.RecvData = ""
##         return temp
##      else:
##         return False # return False if data is not available
##
##   # Send data to client
##   def handle_write(self):
##      try:
##         send_byte = self.send(bytes(self.SendData,'UTF-8'))
##         # Send data
##         if send_byte > 0:
##            send_out = self.SendData[:send_byte]
##            self.SendData = self.SendData[send_byte:]
##            self.handle_write()
##         else: # All data sent out
##            self.SendData = ""
##      except Exception as ex:
##         self.counter += 1
##         print("Data transmission error. Error:",type(ex).__name__,ex.args)
##         if(self.counter >= 4): # transmission error exist for 4 times, consider the connection is lost
##            self.Connect = False
##            self.counter = 0

##   # Not actively write to the client
##   def writable(self):
##      return False
##
##   # socket closing
##   def handle_close(self):
##      print ("close connection")
##      self.Connect = False
##      self.close()
##
### Thread to wait for client connection
##class listen_client_thread(threading.Thread):
##   def __init__(self,port):
##      self.agentServer = AgentServer(port)
##      threading.Thread.__init__ (self)
##
##   def run(self):
##      print ("Listen Client ...")
##      asyncore.loop()
##
### Data input thread
##class input_thread(threading.Thread):
##   def __init__(self,listen_thread):
##      self.listen_thread = listen_thread # listen to client
##      self.data = False
##      threading.Thread.__init__(self)
##
##   def run(self):
##      while 1:
##         try:
##            if(not self.listen_thread.agentServer.clientSocket.Connect):
##               print("Client is not connected")
##               time.sleep(2)
##         except AttributeError:
##            print("Client is not available")
##            time.sleep(2)
##      
##   def write(self,msg):
##      # write to the client
##      try:
##         if(self.listen_thread.agentServer.clientSocket.Connect):
##            #print("Send:",msg)
##            self.listen_thread.agentServer.clientSocket.SendData = msg
##            self.listen_thread.agentServer.clientSocket.handle_write()
##            return True
##      except AttributeError: # Occur when first connect to client or lost the client socket
##         print("No Client is available")
##         time.sleep(2) # slow down the error decision
##         return False
##
##   def read(self):
##      try:
##         if(self.listen_thread.agentServer.clientSocket.Connect):
##            self.data = self.listen_thread.agentServer.clientSocket.data_recv()
####            print("Return:",self.data)
##      except AttributeError: # Occur when first connect to client or lost the client socket
##         print("Read Data Error/No Client is available")
##         time.sleep(2) # slow down the error decision
##      return self.data


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

if __name__ == "__main__":
   # write strace shell file
   traceFile = open("trace.sh","w")
   temp = 'strace -f -e write -p'+str(os.getpid())+' 2>&1 | grep --color "\\".*\\""'
   traceFile.write(temp)
   traceFile.close()

   #----------------------------Client Connection Setup
   # Server Thread setup
##   listen_thread = listen_client_thread(Server_port)
##   listen_thread.daemon = True
##   listen_thread.start()
##   # Client Handler and input thread setup
##   client = input_thread(listen_thread)
##   client.daemon = True
##   client.start()

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
##                  try:
##                     client.write(info) 
##                  except AttributeError:
##                     print("Client is not connected when sending data.")
##               elif info[0] == 0xF5 or info[0] == 0xF7 or info[0] == 0xF9:
##                  upwardDataArr = []
##                  if info[0] == 0xF5: # Arduino 2
##                     upwardDataArr.append(0xF5)
##                  elif info[0] == 0xF7: # Arduino 1
##                     upwardDataArr.append(0xF7)
##                  elif info[0] == 0xF9: # Arduino 1
##                     upwardDataArr.append(0xF9)
##                  detail = serialNo[i].read(12)
##                  for num in detail:
##                     upwardDataArr.append(num)
##                  if upwardDataArr:
##                     upwardData = ''
##                     for num in upwardDataArr:
##                        upwardData += chr(int(num))                        
##                     try:
##                        client.write(upwardData)
##                     except AttributeError:
##                        print("Client is not connected when sending data.")
##            else:
##                sys.exit('No input buffer data exist')
         except serial.serialutil.SerialException:
            print("Serial Error Occur, Port: ",i)
            name = '/dev/ttyUSB'+str(i)
            serialNo[i] = serialReconnect(name)
      print(serialStatus[0],serialStatus[1],serialStatus[2],serialStatus[3])
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
   sendPID = False
   while 1:
      # determine whether client is connected
##      try:
##          if(not client.listen_thread.agentServer.clientSocket.Connect):
##            continue
##      except AttributeError:
##          continue
##         
      # Timer for request PID return
      tempTime = int(round(time.time()*1000))
      if (tempTime - curTime) >= 500:
         serialMap[0].write(bytearray([0xFA,0xFB,0xFE]))
         serialMap[1].write(bytearray([0xFC,0xFD,0xFF]))
         curTime = tempTime

      upwardDataArr = []
      
      # Serial Read loop
      for i in range(2):
         #if i < 2: continue
         #if i == 0:continue
         serialTemp = serialMap[i] # Temp for current Arduino
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
               
               
               elif info[0] == 0xE1: # Arduino 3 now Bluetooth
                  detail = serialTemp.read(7)
                  upwardDataArr.append(0xE1)
                  for num in detail:
                     upwardDataArr.append(num)
                  info += bytes(detail)
                  serialMap[2] = serialTemp
                  if(not serialStatus[2]):
                     print("Serial No: 3 Port:",serialMap[2].port,"is online")
                  serialStatus[2] = True
                  serialName[2] = serialMap[2].port
                  # try to write to client (now at the end of the if-condition)
##                  try:
##                     client.write(str(info)) 
##                  except AttributeError:
##                     print("Client is still not connected.")
               elif info[0] == 0xE2: # Arduino 1
                  pitch = serialTemp.read(2)
                  roll = serialTemp.read(2)
                  upwardDataArr.append(0xE2)
                  for num in pitch:
                     upwardDataArr.append(num)
                  for num in roll:
                     upwardDataArr.append(num)
                  a1Bool[2] = True
               elif info[0] == 0xE3: # Arduino 1
                  motor[0] = serialTemp.read(2)
                  motor[1] = serialTemp.read(2)
                  motorValue[0] = True
               elif info[0] == 0xE4: # Arduino 2
                  yaw = serialTemp.read(2)
                  upwardDataArr.append(0xE4)
                  for num in yaw:
                     upwardDataArr.append(num)
                  a1Bool[1] = True
               elif info[0] == 0xE5: # Arduino 2
                  motor[2] = serialTemp.read(2)
                  motor[3] = serialTemp.read(2)
                  motor[4] = serialTemp.read(2)
                  motor[5] = serialTemp.read(2)
                  motorValue[1] = True
               elif info[0] == 0xE6: # Arduino 1
                  depth = serialTemp.read(2)
                  upwardDataArr.append(0xE6)
                  for num in depth:
                     upwardDataArr.append(num)
                  a1Bool[0] = True
               elif info[0] == 0xE7: # Arduino 1
                  yawSetPoint = serialTemp.read(2)
                  #print(struct.unpack('h',yawSetPoint))
                  upwardDataArr.append(0xE7)
                  for num in yawSetPoint:
                     upwardDataArr.append(num)
               elif info[0] == 0xF5: # Arduino 2
                  detail = serialTemp.read(12)
                  print("Yaw")
                  print(struct.unpack('f',detail[0:4])[0])
                  print(struct.unpack('f',detail[4:8])[0])
                  print(struct.unpack('f',detail[8:12])[0])
                  yawPID.append(0xF5)
                  for num in detail:
                     yawPID.append(num)
                  ybool = True
               elif info[0] == 0xF7: # Arduino 1
                  detail = serialTemp.read(12)
                  print("Depth")
                  print(struct.unpack('f',detail[0:4])[0])
                  print(struct.unpack('f',detail[4:8])[0])
                  print(struct.unpack('f',detail[8:12])[0])
                  depthPID.append(0xF7)
                  for num in detail:
                     depthPID.append(num)
                  dbool = True
               elif info[0] == 0xF9: # Arduino 1
                  detail = serialTemp.read(12)
                  print("Pitch")
                  print(struct.unpack('f',detail[0:4])[0])
                  print(struct.unpack('f',detail[4:8])[0])
                  print(struct.unpack('f',detail[8:12])[0])
                  pitchPID.append(0xF9)
                  for num in detail:
                     pitchPID.append(num)
                  pbool = True
               
                  
               # print depth, yaw, pitch, roll if all arrived
               if(a1Bool[0] and a1Bool[1] and a1Bool[2]):
                  print('Depth:',struct.unpack('h',depth))
                  print('Yaw:',struct.unpack('h',yaw))
                  print('Pitch:',struct.unpack('h',pitch))
                  print('Roll:',struct.unpack('h',roll))
                  a1Bool = [False,False,False]                  
               
               # print motor value if all arrived
               if(motorValue[0] and motorValue[1]):
                  for m in range(6):
                     print('Motor',m+1,':',struct.unpack('h',motor[m]))
                  motorValue[0] = False
                  motorValue[1] = False

               if(sendPID and pbool and ybool and dbool):
                  for num in pitchPID:
                     upwardDataArr.append(num)
                  for num in depthPID:
                     upwardDataArr.append(num)
                  for num in yawPID:
                     upwardDataArr.append(num)

##               if sendPID == False:
##                  if (pbool and dbool and ybool):
##                     for num in yawPID:
##                        upwardDataArr.append(num)
##                     for num in depthPID:
##                        upwardDataArr.append(num)
##                     for num in pitchPID:
##                        upwardDataArr.append(num)
##                     print('sendPID')
##                     pbool = False
##                     dbool = False
##                     ybool = False
##                     sendPID = True
##               else:
##                  if pbool:
##                     for num in pitchPID:
##                        upwardDataArr.append(num)
##                     pbool = False
##                  if dbool:
##                     for num in depthPID:
##                        upwardDataArr.append(num)
##                     dbool = False
##                  if ybool:
##                     for num in yawPID:
##                        upwardDataArr.append(num)
##                     ybool = False
                  
         except serial.serialutil.SerialException:
            print("Serial Error Occur, Port: ",writeTo)
            serialTemp = serialReconnect(serialName[writeTo])
            serialTemp.write(command)
            
      # check serial status
      serialDisable(otherPort,otherPortName)

      # send data to client
##      if upwardDataArr:
##         upwardData = ''
##         for num in upwardDataArr:
##            upwardData += chr(int(num))
##         client.write(upwardData)

      # receive data from client
      data = []
      data +=bytearray([0xB1])
      data +=struct.pack('h',int(0))
      data +=bytearray([0x00])
      tempList = []
      print(data)
      if not data: continue
##      print(data)
      
      # Translate data back to bytearray
##      tempList = []
##      for i in data.decode('utf-8'):
####          print(ord(i))
##          tempList.append(ord(i))
##      data = bytearray(tempList)

      #Decode protocol from server
##      print(len(data))
      i = 0 # for record the current byte read
      while i < len(data):
         writeTo = -1 # determine which serial to write
         if data[i] == 0xF6: #stop send current PID to onshore
            sendPID = False
            i += 1
            print('F6')
         elif data[i] == 0xA1:
            forward = data[i:i+3]
            i += 3
            print('A1')
##            print('i:',i)
            writeTo = 0
         elif data[i] == 0xA3 or data[i] == 0xA5:
            forward = data[i:i+2]
            writeTo = 0
            if data[i] == 0xA3: print('A3')
            else: print('A5')
            i += 2
##            print('i:',i)
         elif data[i] == 0xAB or data[i] == 0xAD:
            forward = data[i:i+2]
            writeTo = 0
            if data[i] == 0xAB: print('AB')
            else: print('AD')
            i += 2
         elif data[i] == 0xAC:
            forward = bytearray([data[i]])
            writeTo = 0
            print('AC')
            i += 1
         elif data[i] == 0xA7 or data[i] == 0xA9:
            forward = data[i:i+13]
            if data[i] == 0xA7:
               print('A7')
               dbool = False
               depthPID = []
            else:
               print('A9')
               pbool = False
               pitchPID = []
            i += 13
##            print('i:',i)
            writeTo = 0
            sendPID = True
         elif data[i] == 0xB1:
            forward = data[i:i+4]
            print('B1')
##            for num in range(4):
##               print(data[num+i])
            print('Angle:',struct.unpack('h',bytearray([forward[1],forward[2]])))
            print('Mag:',forward[3])
            i += 4
##            print('i:',i)
            writeTo = 1
            
         elif data[i] == 0xB3:
            forward = data[i:i+3]
            print('B3')
            print('Y:',struct.unpack('h',forward[1:3]))
            i += 3
##            print('i:',i)
            writeTo = 1            
         elif data[i] == 0xB5:
            forward = data[i:i+13]
            print('B5')
            i += 13
##            print('i:',i)
            writeTo = 1
            sendPID = True
            ybool = False
            yawPID = []
         elif data[i] == 0xB7:
            forward = data[i:i+2]
            writeTo = 1
            print('B7')
            i += 2
         elif data[i] == 0xC1:
            forward = data[i:i+9]
            print('C1')
            i += 9
##            print('i:',i)
            writeTo = 2            
         elif data[i] == 0xD1:
            forward = data[i:i+3]
            print('D1')
            i += 3
##            print('i:',i)
            writeTo = 3
         elif data[i] == 0xD2:
            forward = data[i:i+8]
            print('D2')
            i += 8
##            print('i:',i)
            writeTo = 3
         elif data[i] == 0xF4:
            forward = bytearray([data[i]])
            print('F4')
            sendPID = True
            pitchPID = []
            depthPID = []
            yawPID = []
            pbool = False
            dbool = False
            ybool = False
            writeTo = [0,1]
            i += 1
         else:
            i += 1
##            print('i:',i)

         # write to corresponding serial port
##         if(writeTo in [-1]):
         #print(writeTo)
         if (type(writeTo) is list):
            for i in writeTo:
               try:
                  print(forward)
                  #time.sleep(2)
                  serialMap[i].write(bytes(forward))
               except serial.serialutil.SerialException:
                  print("Serial ",i," Port:",serialName[i]," is disconnected")
                  serialStatus[i] = False
                  serialTemp = serialReconnect(serialName[i])
                  serialTemp.write(command)
         elif(writeTo > -1):
            #print(forward)
            #writeTo -= 1
            try:
               print(forward)
               #time.sleep(2)
               #tempForward=''.join(forward)
               serialMap[writeTo].write(bytes(forward))
            except serial.serialutil.SerialException:
               print("Serial ",writeTo," Port:",serialName[writeTo]," is disconnected")
               serialStatus[writeTo] = False
               serialTemp = serialReconnect(serialName[writeTo])
               serialTemp.write(command)
##         print("End: ",forward)
         forward=[]
         time.sleep(5)
