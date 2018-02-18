# command for get arduino type
arduinoInfoCommand = bytearray([0xF1])

# motor variable
motorValue = [False,False]
motor = [0,0,0,0,0,0]

#depth, yaw, (pitch, roll) variable
depth = 0
yaw = 0
pitch = 0
row = 0

pitchPid = False
yawPid = False

yawSetPoint = 0

stage = [False,False,False,False]

Arduinobuffer = []
