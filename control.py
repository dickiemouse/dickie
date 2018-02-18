import struct
import threading
import storage

class control_thread(threading.Thread):
   def __init__(self):
      threading.Thread.__init__ (self)

   def run(self):
       path()

forward = storage.Arduinobuffer

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
