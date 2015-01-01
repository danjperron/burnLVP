###############################
#
#  GPIO definition interface for RaspBerry Pi
#
#  Put All your pin definition here
#  All class will use this file for reference
#
#

import RPi.GPIO as GPIO
from time import sleep

global PIC_CLK
global PIC_DATA
global PIC_MCLR
global PIC_PGM
#CLK GPIO
PIC_CLK = 7

# Its not wise to change GPIO pins used here, e.g pin 5 was not working as input
#DATA GPIO 
PIC_DATA = 24

#MCLR GPIO
PIC_MCLR = 21

#PGM
PIC_PGM = 26

# Only implemented if the same pin is used to read & write data
def setDataModeRead() :
  GPIO.setup(PIC_DATA,GPIO.IN)

# Only implemented if the same pin is used to read & write data
def setDataModeWrite() :
  GPIO.setup(PIC_DATA,GPIO.OUT)

def getDataState() :
  return GPIO.input(PIC_DATA)

def setDataState( turnOn) :
  GPIO.output(PIC_DATA, turnOn)

def setClockState( turnOn) :
  GPIO.output(PIC_CLK, turnOn)

def setPGMState( turnOn ) :
  GPIO.output(PIC_PGM, turnOn)


def setMCLRState( turnOn) :
  GPIO.output(PIC_MCLR, turnOn)


def clockInterval( multiplier=1):
  for loop in range( multiplier) :
    pass
    sleep(0.001)

def Setup_Interface():
  GPIO.setwarnings(True)
  GPIO.setmode(GPIO.BOARD)
  GPIO.setup(PIC_MCLR,GPIO.OUT)
  GPIO.output(PIC_MCLR,False)
  GPIO.setup(PIC_CLK,GPIO.OUT)
  GPIO.setup(PIC_DATA,GPIO.OUT)
  GPIO.setup(PIC_PGM,GPIO.OUT)
