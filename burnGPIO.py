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


# check CHIP or it is a raspberry Pi

f = open('/proc/cpuinfo','r')
cpuinfo = f.read()
f.close()


if cpuinfo.find('Allwinner') >0 :
   #  ------  chip  ------
   print('C.H.I.P GPIO')
   import CHIP_IO.GPIO as GPIO
   GPIO.cleanup()
   #CLK GPIO
   PIC_CLK = 'LCD-D15'

   #DATA GPIO 
   PIC_DATA = 'LCD-D19'

   #MCLR GPIO
   PIC_MCLR = 'LCD-D21'

   #PGM
   PIC_PGM = 'LCD-D23'

else:
   #  ------ Raspberry Pi --
   print('Raspberry Pi GPIO')
   import RPi.GPIO as GPIO

   #CLK GPIO
   PIC_CLK = 7

   #DATA GPIO 
   PIC_DATA = 24

   #MCLR GPIO
   PIC_MCLR = 21

   #PGM
   PIC_PGM = 26




def Setup_Interface():
  GPIO.setwarnings(False)
  GPIO.setmode(GPIO.BOARD)
  GPIO.setup(PIC_MCLR,GPIO.OUT)
  GPIO.output(PIC_MCLR,False)
  GPIO.setup(PIC_CLK,GPIO.OUT)
  GPIO.setup(PIC_DATA,GPIO.OUT)
  GPIO.setup(PIC_PGM,GPIO.OUT)
  


