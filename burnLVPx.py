#!/usr/bin/env python

################################
#
# burnLVP.py Version 2.0
#
#
# Program to burn pic12, pic16 and pic18 Microchip cpu
#
#
# programmer : Daniel Perron
# Date       : Sept 17, 2013
# Version    : 0.001
#
# Enhanced version of  burnLVP  for pic18F...
#
# source code:  https://github.com/danjperron/A2D_PIC_RPI
#
#
#
#  18 Sept. update   
#                   Bulk Erase works with adafruit level converter if power is 4.5 V
#                   Code erase function working
#                   Code blank check working
#                   Code programming multi-Panel working
#                   Code check working
#
#  19 sept. update :
#                    EEROM DATA programming and checking  complete
#                    ID and config programming and checking complete
#                    Add generic function to implement other Pic18 family
#
#  26 sept :        Use class to create function specific to cpu family .
#
#  19 dec. 2014:    Add PIC18F2_4XK22 class.  programmer: Pascal Sandrez

#////////////////////////////////////  MIT LICENSE ///////////////////////////////////
#	The MIT License (MIT)
#
#	Copyright (c) 2013 Daniel Perron
#
#	Permission is hereby granted, free of charge, to any person obtaining a copy of
#	this software and associated documentation files (the "Software"), to deal in
#	the Software without restriction, including without limitation the rights to
#	use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
#	the Software, and to permit persons to whom the Software is furnished to do so,
#	subject to the following conditions:
#
#	The above copyright notice and this permission notice shall be included in all
#	copies or substantial portions of the Software.
#
#	THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#	IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
#	FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
#	COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
#	IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
#	CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


import sys, termios, atexit
from intelhex import IntelHex
from select import select   

#=======   I/O interface
import burnGPIO as IO


#=======  Pic Family Class import

#import burnLVP_Pic12
from CpuPIC12      import PIC12
from CpuPIC18FXX2  import PIC18FXX2
from CpuPIC18F2XXX import PIC18F2XXX
from CpuPIC18FXXK80 import PIC18FXXK80
from CpuPIC18F2_4XK22 import PIC18F2_4XK22
pic12     = PIC12()
pic18fxx2 = PIC18FXX2()
pic18f2xxx = PIC18F2XXX()
pic18fxxk80 = PIC18FXXK80()
pic18f2_4xk22 = PIC18F2_4XK22()
AllCpuFamily = [pic12,pic18fxx2,pic18f2xxx,pic18fxxk80,pic18f2_4xk22]

#=============  main ==========


if __name__ == '__main__':
  if len(sys.argv) is 2:
    HexFile = sys.argv[1]
  elif len(sys.argv) is 1:
    HexFile = ''
  else:
    print 'Usage: %s file.hex' % sys.argv[0]
    quit()


## load hex file if it exist
FileData =  IntelHex()
if len(HexFile) > 0 :
   try:
     FileData.loadhex(HexFile)
   except IOError:
     print 'Error in file "', HexFile, '"'
     quit()

PicData = FileData.todict()       
print 'File "', HexFile, '" loaded'


#try to figure out the CpuId by scanning all available Cpu family
IO.Setup_Interface()

CpuId=0
print "Scan CPU "

for l in AllCpuFamily:
  CpuTag = l.ScanCpuTag()
  if(CpuTag!=0):
    #found the correct cpu
    print "Cpu Id   =", hex(l.CpuId)
    print "Revision = ", hex(l.CpuRevision)
    #ok set the cpu family who find the cpu
    CpuF=l
    break;
  else:
    l.Release_LVP() 

if CpuTag == 0:
  print " Unable to identify cpu type"
  quit()

#now let's find the Cpu Family

CpuInfo=None
for l in AllCpuFamily:
  CpuInfo = l.FindCpu(CpuTag)
  if CpuInfo != None:
    print "Found ", CpuInfo[0], "from Cpu Family ",l.PicFamily
    print "Cpu Id:", hex(l.CpuId), " revision:", l.CpuRevision 
    CpuF = l
    break;

if CpuInfo==None:
  print "Unable to continue... Unable to handle this cpu"
  print "Cpu Id:", hex(CpuTag & 0xFFE0)
  CpuF.Release_LVP()
  quit()





#ok let's start to program
#LVP mode should be okay since we found the cpu
#

#

CpuF.BulkErase()
if CpuF.ProgramBlankCheck():
  if CpuF.DataBlankCheck():
    CpuF.ProgramBurn(PicData)
    if CpuF.ProgramCheck(PicData):
       CpuF.DataBurn(PicData)
       if CpuF.DataCheck(PicData):
         CpuF.IDBurn(PicData)
         if CpuF.IDCheck(PicData):
           CpuF.ConfigBurn(PicData)
           if CpuF.ConfigCheck(PicData):
             print "Program verification passed!" 

#release LVP and force reset
#CpuF.MemoryDump(CpuF.ConfigBase,14)
CpuF.Release_LVP()










