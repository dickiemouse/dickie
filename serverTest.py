import threading
import controlTest as cTest
import time
import globalVariable


class server_thread(threading.Thread):
   def __init__(self):
      threading.Thread.__init__ (self)

   def run(self):
       while True:
           if not(len(globalVariable.forward)==0):
               print (globalVariable.forward)
               del globalVariable.forward[0]

class control_thread(threading.Thread):
   def __init__(self):
      threading.Thread.__init__ (self)

   def run(self):
       cTest.path()

if __name__ == "__main__":
    server = server_thread()
    server.daemon = False
    server.start()
    control = control_thread()
    control.daemon = True
    control.start()
    time.sleep(2)
