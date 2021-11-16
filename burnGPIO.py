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


global PIC_CLK
global PIC_DATA
global PIC_MCLR
global PIC_PGM


import RPi.GPIO as GPIO

#CLK GPIO
PIC_CLK = 7
#DATA GPIO
PIC_DATA = 24
#MCLR GPIO
PIC_MCLR = 21
#PGM
PIC_PGM = 26


# C.H.I.P. is obsolete
# then MGPIO is removed
# only works for PI



def Setup_Interface():
  GPIO.setwarnings(False)
  GPIO.setmode(GPIO.BOARD)
  GPIO.setup(PIC_MCLR,GPIO.OUT)
  GPIO.output(PIC_MCLR,False)
  GPIO.setup(PIC_CLK,GPIO.OUT)
  GPIO.setup(PIC_DATA,GPIO.OUT)
  GPIO.setup(PIC_PGM,GPIO.OUT)


