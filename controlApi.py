import math
import struct
import asyncore, socket
import threading
import time
import random, os, sys

# Arduino no.0

setDepthByte = [0xA1] # short depth_setPoint [3 bytes]	(depth unit : cm)

setDepthPidOnByte = [0xAB]

getDepthValueByte = [0xAC]

getThruster2Byte = [0xFB]

getDepthBtye = [0xFE]

# Arduino no.1

moveByte = [0xB1] # short angle + byte magnitude [4 bytes] (angle: From -180 to 180 degree , magnitude : 0 - 255)

setYawBtye = [0xB3]

setYawPidOnByte = [0xB7]

getYawByte = [0xFC]

getThruster4Byte = [0xFD]

getYawValueBtye = [0xFF]

sendToArduino0 = [0xA1,0xAB,0xAC,0xFB,0xFE]
sendToArduino1 = [0xB1,0xB3,0xB7,0xFC,0xFD,0xFF]

def move(angle,magnitude):
    command = []
    command += bytearray(moveByte)
    command += struct.pack('h',int(angle))
    command += struct.pack('b',int(magnitude))
    forward = command[0:4]
    return bytes(forward)

def setDepth(depth):
    command = []
    command += bytearray(setDepthByte)
    command += struct.pack('h',int(depth))
    forward = command[0:3]
    return bytes(forward)
    
def setDepthPidOn(depthPidIsOn):
    command = []
    command += bytearray(setDepthPidOnByte)
    command += struct.pack('?',depthPidIsOn)
    forward = command[0:2]
    print(command)
    return bytes(forward)

def getDepthValue():
    return bytes(bytearray(getDepthValueByte)) 

def getDepth():
    return bytes(bytearray(getDepthBtye))

def getThruster2():
    return bytes(bytearray(getThruster2Byte))

def setYaw(angle):
    command = []
    command += bytearray(setYawByte)
    command += struct.pack('h',int(angle))
    print(command)
    forward = command[0:3]
    return bytes(forward)

def setYawPidOn(yawPidIsOn):
    command = []
    command += bytearray(setYawPidOnByte)
    command += struct.pack('?',yawPidIsOn)
    forward = command[0:2]
    print(command)
    return bytes(forward)

def getYaw():
    return bytes(bytearray(getYawByte))

def getThruster4():
    return bytes(bytearray(getThruster4Byte))

def getYawValue():
    return bytes(bytearray(getYawValueBtye))
