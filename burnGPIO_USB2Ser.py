###############################
#  GPIO definition interface for USB to Serial Converter
#
#
#
import serial
import threading
from time import sleep

global serialPort
global txdOn

txdOn = False

# Only implemented if the same pin is used to read & write data
def setDataModeRead() :
  pass

# Only implemented if the same pin is used to read & write data
def setDataModeWrite() :
  pass

def getDataState() :
  global serialPort
  return serialPort.getCTS()

def setDataState( turnOn) :
  global serialPort
  serialPort.setRTS( turnOn)

def setClockState( turnOn) :
  global serialPort
  serialPort.setDTR( turnOn)

def setPGMState( turnOn ) :
  global serialPort
  global txdOn
  # works in latch mode with an external latch circuit connected. Can't be turned off tho.
  #if turnOn :
  #  serialPort.write( b'\x00' )
  
  # Also works in toggle mode with external flip-flop. Use only diode and 10K R, no capacitors needed.
  # writing 00 results in a high state on the tx line.
  if turnOn != txdOn :
    serialPort.write( b'\x00' )
    txdOn = turnOn


def setMCLRState( turnOn) :
  pass


def clockInterval( multiplier=1):
  # For USB-Serial interface, we reads/writes need a delay of 5ms
  sleep(0.005 * multiplier)

def Setup_Interface():
  global serialPort
  # in order to control rtscts manually, they have to be 0 here
  serialPort = serial.Serial('/dev/ttyUSB0', 19200, timeout=0,                
    parity=serial.PARITY_NONE, rtscts=0, dsrdtr=0 )
  setDataState( False)
  setClockState( False)
  

def Release_Interface():
  global serialPort
  serialPort.close()
