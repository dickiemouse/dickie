import struct
import storage as storage

# Arduino no.0

setDepthByte = [0xA1] # short depth_setPoint [3 bytes]	(depth unit : cm)

setPitchByte = [0xA3]

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

sendToArduino0 = [0xA1,0xA3,0xAB,0xAC,0xAD,0xFA,0xFB,0xFE]
sendToArduino1 = [0xB1,0xB3,0xB7,0xFC,0xFD,0xFF]

def move(angle,magnitude):
    command = []
    command += bytearray(moveByte)
    command += struct.pack('h',int(angle))
    command += struct.pack('b',int(magnitude))
    storage.arduinoBuffer.append(command[0:4])

def setDepth(depth):
    command = []
    command += bytearray(setDepthByte)
    command += struct.pack('h',int(depth))
    storage.arduinoBuffer.append(command[0:3])

def setPitch(pitch):
    command = []
    command += bytearray(setPitchByte)
    command += struct.pack('b',int(pitch))
    storage.arduinoBuffer.append(command[0:2])

def setDepthPidOn(depthPidIsOn):
    command = []
    command += bytearray(setDepthPidOnByte)
    command += struct.pack('h',int(depthPidIsOn))
    storage.arduinoBuffer.append(command[0:2])

def setPitchPidOn(pitchPidIsOn):
    command = []
    command += bytearray(setPitchPidOnByte)
    command += struct.pack('h',int(pitchPidIsOn))
    storage.arduinoBuffer.append(command[0:2])

def calDepth():
    storage.arduinoBuffer.append(bytearray(calDepthByte))

def getPitchRoll():
    storage.arduinoBuffer.append(bytearray(getPitchRollBtye))
    storage.arduinoBuffer.append(bytearray(getPitchRollBtye))

def getDepth():
    storage.arduinoBuffer.append(bytearray(getDepthBtye))

def getThruster2():
    storage.arduinoBuffer.append(bytearray(getThruster2Byte))

def setYaw(angle):
    command = []
    command += bytearray(setYawByte)
    command += struct.pack('h',int(angle))
    storage.arduinoBuffer.append(command[0:3])

def setYawPidOn(yawPidIsOn):
    command = []
    command += bytearray(setYawPidOnByte)
    command += struct.pack('h',int(yawPidIsOn))
    storage.arduinoBuffer.append(command[0:2])

def getYaw():
    storage.arduinoBuffer.append(bytearray(getYawByte))

def getThruster4():
    storage.arduinoBuffer.append(bytearray(getThruster4Byte))

def getYawValue():
    storage.arduinoBuffer.append(bytearray(getYawValueBtye))
