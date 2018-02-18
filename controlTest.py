import struct
import globalVariable
import time

forward = globalVariable.forward

def path():
    command = []
    command += bytearray([0xA0])
    command += struct.pack('h',int(120))
    command += struct.pack('b',int(100))
    forward.append(command[0:4])
    command = []
    command += bytearray([0xA0])
    command += struct.pack('h',int(120))
    command += struct.pack('b',int(100))
    forward.append(command[0:4])
    command = []
    command += bytearray([0xA0])
    command += struct.pack('h',int(120))
    command += struct.pack('b',int(100))
    forward.append(command[0:4])
