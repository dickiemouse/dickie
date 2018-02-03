import struct
import serial

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

command=bytearray([0xf1])
serial=serialReconnect('/dev/ttyUSB1')

while 1:
   serial.write(command)
   try:
      print('serial:',serial.inWaiting())
      if(serial.inWaiting() >= 2):
         info = serial.read(1)
         if info[0] == 0xF2:
            detail = serial.read(1)
            sNum = serialNumber(detail[0])
            print(sNum)
            if sNum==0:
              break
   except:
      print('false')
while 1:
   command=bytearray([0xfa])
   serial.write(command)
   if(serial.inWaiting() >= 5):
      info = serial.read(1)
      if info[0] == 0xE2:
         pitch = serial.read(2)
         roll = serial.read(2)
         print('pitch:',struct.unpack('h',pitch))
         print('roll:',struct.unpack('h',roll))

