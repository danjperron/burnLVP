###############################
#
#  burnGPIO.py
#
#  GPIO definition interface
#
#  Put All your pin definition here
#  All class will use this file for reference
#
#
import serial
import threading
from time import sleep

global serialPort
global PGMThread

PGMThread = None

# Only used if the same pin is used to read & write data
def setDataModeRead() :
  pass

# Only used if the same pin is used to read & write data
def setDataModeWrite() :
  pass

def getDataState() :
  global serialPort
  return serialPort.getCTS()

def setDataState( onOff) :
  global serialPort
  serialPort.setRTS( onOff)

def setClockState( onOff) :
  global serialPort
  serialPort.setDTR( onOff)

def setPGMState( onOff ) :
  global serialPort
  global PGMThread
  # The advantage of setting txd line high using software is that no external hardware is needed
  # However, it does not work, probably the voltage rises too slowly for PGM.
  # So again, some external Xsistor circuit would have to be used
  if onOff :
    PGMThread = TxdOnThread( serialPort)
    PGMThread.start()
  else :
    if PGMThread is not None :
      PGMThread.stop()

class TxdOnThread(threading.Thread):
     def __init__(self,serialPort):
         super(TxdOnThread, self).__init__()
         self.serialPort=serialPort
         self.running = True

     def run(self):
         while( self.running) :
           self.serialPort.write( b'\x00' )

     def stop(self):
       self.running = False


def setMCLRState( onOff) :
  pass


def clockInterval( multiplier=1):
  # For USB-Serial interface, we reads/writes need a delay of 5ms
  sleep(0.005 * multiplier)

def Setup_Interface():
  global serialPort
  # in order to control rtscts manually, they have to be 0 here
  serialPort = serial.Serial('/dev/ttyUSB1', 19200, timeout=0,                
    parity=serial.PARITY_NONE, rtscts=0, dsrdtr=0 )
  setDataState( False)
  setClockState( False)
  

def Release_Interface():
  global serialPort
  serialPort.close()
