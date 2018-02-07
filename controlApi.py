import math
import struct
import asyncore, socket
import threading
import time
import serial
import random, os, sys
import server as server

# Arduino no.0

setDepthByte = [0xA1] # short depth_setPoint [3 bytes]	(depth unit : cm)

setDepthPidOnByte = [0xAB]

calDepthByte = [0xAC]

setPitchPidOnByte = [0xAD]

getPitchRollBtye = [0xFA]

getThruster2Byte = [0xFB]

getDepthBtye = [0xFE]

# Arduino no.1

moveByte = [0xB1] # short angle + byte magnitude [4 bytes] (angle: From -180 to 180 degree , magnitude : 0 - 255)

setYawBtye = [0xB3]

setYawPidOnByte = [0xB7]

getYawByte = [0xFC]

getThruster4Byte = [0xFD]

getYawValueBtye = [0xFF]

sendToArduino0 = [0xA1,0xAB,0xAC,0xAD,0xFA,0xFB,0xFE]
sendToArduino1 = [0xB1,0xB3,0xB7,0xFC,0xFD,0xFF]

def move(angle,magnitude):
    command = []
    command += bytearray(moveByte)
    command += struct.pack('h',int(angle))
    command += struct.pack('b',int(magnitude))
    forward = command[0:4]
    send(bytes(forward))

def setDepth(depth):
    command = []
    command += bytearray(setDepthByte)
    command += struct.pack('h',int(depth))
    forward = command[0:3]
    send(bytes(forward))

def setDepthPidOn(depthPidIsOn):
    command = []
    command += bytearray(setDepthPidOnByte)
    command += struct.pack('h',int(depthPidIsOn))
    forward = command[0:2]
    print(command)
    send(bytes(forward))

def setPitchPidOn(pitchPidIsOn):
    command = []
    command += bytearray(setPitchPidOnByte)
    command += struct.pack('h',int(pitchPidIsOn))
    forward = command[0:2]
    send(bytes(forward))

def calDepth():
    send(bytes(bytearray(calDepthByte)))

def getPitchRoll():
    send(bytes(bytearray(getPitchRollBtye)))
    receive(bytes(bytearray(getPitchRollBtye)))

def getDepth():
    send(bytes(bytearray(getDepthBtye)))
    receive(bytes(bytearray(getDepthBtye)))

def getThruster2():
    send(bytes(bytearray(getThruster2Byte)))
    receive(bytes(bytearray(getThruster2Byte)))

def setYaw(angle):
    command = []
    command += bytearray(setYawByte)
    command += struct.pack('h',int(angle))
    print(command)
    forward = command[0:3]
    send(bytes(forward))

def setYawPidOn(yawPidIsOn):
    command = []
    command += bytearray(setYawPidOnByte)
    command += struct.pack('h',int(yawPidIsOn))
    forward = command[0:2]
    print(command)
    send(bytes(forward))

def getYaw():
    send(bytes(bytearray(getYawByte)))
    receive(bytes(bytearray(getYawByte)))

def getThruster4():
    send(bytes(bytearray(getThruster4Byte)))
    receive(bytes(bytearray(getThruster4Byte)))

def getYawValue():
    send(bytes(bytearray(getYawValueBtye)))
    receive(bytes(bytearray(getYawValueBtye)))

def send(forward):
    writeTo = -1
    try:
       if(forward[0] in sendToArduino0):
          writeTo = 0
          server.serialMap[0].write(bytes(forward))
       elif(forward[0] in sendToArduino1):
          writeTo = 1
          server.serialMap[1].write(bytes(forward))
    except serial.serialutil.SerialException:
       if (writeTo != -1):
           print("Serial ",writeTo," Port:",server.serialName[writeTo]," is disconnected")
           server.serialStatus[writeTo] = False
           serialTemp = server.serialReconnect(serialName[writeTo])
           serialTemp.write(command)

def receive(forward):
    # Serial Read loop
    received = False
    if(forward[0] in sendToArduino0):
        receivedFrom = 0
    elif(forward[0] in sendToArduino1):
        receivedFrom = 1
    while not (received):
        serialTemp = server.serialMap[receivedFrom] # Temp for current Arduino
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
                    server.serialMap[sNum] = serialTemp
                    # if different from orignal port, record and erase another one by serialDisable Function
                    if(server.serialName[sNum] != server.serialMap[sNum].port):
                       otherPort = sNum
                       otherPortName = serialName[sNum]
                    server.serialName[sNum] = server.serialMap[sNum].port
                    if(not server.serialStatus[sNum]):
                       print("Serial No:",sNum+1," Port:",server.serialMap[sNum].port,"is online")
                    server.serialStatus[sNum] = True
              elif info[0] == 0xE3: # Arduino 1
                 motor[0] = struct.unpack('h',serialTemp.read(2))[0]
                 motor[1] = struct.unpack('h',serialTemp.read(2))[0]
                 motorValue[0] = True
                 print('Motor 0:',motor[0],'Motor 1:', motor[1])
                 received = True
              elif info[0] == 0xE4: # Arduino 2
                 yaw = struct.unpack('h',serialTemp.read(2))[0]
                 a1Bool[1] = True
                 print('Yaw is:',yaw)
                 received = True
              elif info[0] == 0xE5: # Arduino 2
                 motor[2] = struct.unpack('h',serialTemp.read(2))[0]
                 motor[3] = struct.unpack('h',serialTemp.read(2))[0]
                 motor[4] = struct.unpack('h',serialTemp.read(2))[0]
                 motor[5] = struct.unpack('h',serialTemp.read(2))[0]
                 motorValue[1] = True
                 print('Motor 2:',motor[2],'Motor 3:',motor[3],'Motor 4:',motor[4],'Motor 5:',motor[5])
                 received = True
              elif info[0] == 0xE6: # Arduino 1
                 depth = struct.unpack('h',serialTemp.read(2))[0]
                 print('depth:',depth)
                 a1Bool[0] = True
                 received = True
              elif info[0] == 0xE7: # Arduino 1
                 yawSetPoint = struct.unpack('h',serialTemp.read(2))[0]
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
