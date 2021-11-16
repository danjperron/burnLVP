#!/usr/bin/env python3

################################
#
# burn18LVP.py
#
#
# Program to burn pic18F...using LVP mode with a Rasberry Pi
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
#                    Add generic function to implement other Pic18 familly
#
#  Next thinsg to do:
#                   Add pic18Fxxx2 pic18Fxxx8 familly
#                   Add pic18Fxxk80 familly


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



from time import sleep
import RPi.GPIO as GPIO
import sys, termios, atexit
from intelhex import IntelHex
from select import select



# some constant

Pic18PanelSize = 0x2000



#set io pin

#CLK GPIO 4
PIC_CLK = 7

#DATA GPIO 8
PIC_DATA = 24

#MCLR GPIO 9
PIC_MCLR = 21

#PGM_GPIO
PIC_PGM  = 26



#compatible PIC id

PIC18F242  = 0x0480
PIC18F248  = 0x0800
PIC18F252  = 0x0400
PIC18F258  = 0x0840
PIC18F442  = 0x04A0
PIC18F448  = 0x0820
PIC18F452  = 0x0420
PIC18F458  = 0x0860



#PIC18 Familly

PIC18FXXX   = 1
PIC18FXXXX  = 2
PIC18FXXKXX = 3




# command definition
C_PIC18_NOP	      = 0b0000
C_PIC18_INSTRUCTION   = 0b0000
C_PIC18_TABLAT 	      = 0b0010
C_PIC18_READ          = 0b1000
C_PIC18_READ_INC      = 0b1001
C_PIC18_READ_DEC      = 0b1010
C_PIC18_READ_PRE_INC  = 0b1011
C_PIC18_WRITE         = 0b1100
C_PIC18_WRITE_INC_BY2 = 0b1101
C_PIC18_WRITE_DEC_BY2 = 0b1110
C_PIC18_START_PGM     = 0b1111


def mydelay():
#   pass
   return

def Set_LVP_PIC18():
   #held MCLR LOW
   GPIO.setup(PIC_MCLR,GPIO.OUT)
   GPIO.output(PIC_MCLR,False)

   #hdel PIC_CLK & PIC_DATA & PIC_PGM low
   GPIO.setup(PIC_CLK, GPIO.OUT)
   GPIO.output(PIC_CLK, False)
   GPIO.setup(PIC_DATA , GPIO.OUT)
   GPIO.output(PIC_DATA, False)
   GPIO.setup(PIC_PGM, GPIO.OUT)
   GPIO.output(PIC_PGM, False)

   sleep(0.01)
   #set PGM High
   GPIO.output(PIC_PGM, True)
   sleep(0.01)
   #Set MCLR High
   GPIO.output(PIC_MCLR, True)
   sleep(0.01)


def Release_LVP_PIC18():
   #set PGM Low
   GPIO.output(PIC_PGM, False)
   sleep(0.1)

   #held MCLR LOW
   GPIO.setup(PIC_MCLR,GPIO.OUT)
   GPIO.output(PIC_MCLR,False)

   #PIC_CLK & PIC_DATA has input
   GPIO.setup(PIC_CLK, GPIO.IN)
   GPIO.setup(PIC_DATA , GPIO.IN)

   sleep(0.1)
   #Set MCLR High
   GPIO.output(PIC_MCLR, True)


def LoadWordPic18(Value):
  GPIO.setup(PIC_DATA,GPIO.OUT)
  for loop in range(16):
     GPIO.output(PIC_DATA,(Value & 1)==1)
     GPIO.output(PIC_CLK,True)
     #mydelay()
     GPIO.output(PIC_CLK,False)
     #mydelay()
     Value = Value >> 1;

def ReadDataPic18():
  GPIO.setup(PIC_DATA,GPIO.IN)
  for loop in range(8):
    GPIO.output(PIC_CLK,True)
    #mydelay()
    GPIO.output(PIC_CLK,False)
    #mydelay()
  Value = 0
  for loop in range(8):
    GPIO.output(PIC_CLK,True)
    #mydelay()
    #mydelay()
    if GPIO.input(PIC_DATA):
        Value =  Value | (1 << loop)
    GPIO.output(PIC_CLK,False)
    #mydelay()
  return Value

def LoadCommandPic18(Value):

  GPIO.setup(PIC_DATA,GPIO.OUT)
  for loop in range(4):
     GPIO.output(PIC_DATA,(Value & 1)==1)
     GPIO.output(PIC_CLK,True)
     #mydelay()
     GPIO.output(PIC_CLK,False)
     #mydelay()
     Value = Value >> 1;

def LoadCommandWordPic18(CommandValue,WordValue):
  LoadCommandPic18(CommandValue)
  LoadWordPic18(WordValue)


def LoadCode(Instruction):
  LoadCommandWordPic18(C_PIC18_INSTRUCTION,Instruction)


def ReadMemoryPic18Next():
  LoadCommandPic18(C_PIC18_READ_INC)
  return ReadDataPic18()



def LoadEepromAddress(EepromAddress):
  LoadCode(0x0E00 | ((EepromAddress >>  8)  & 0xff))
  LoadCode(0x6EAA)
  LoadCode(0x0E00 | (EepromAddress & 0xff))
  LoadCode(0x6EA9)

def LoadMemoryAddress(MemoryAddress):
  LoadCode(0x0E00 | ((MemoryAddress >> 16) & 0xff))
  LoadCode(0x6EF8)
  LoadCode(0x0E00 | ((MemoryAddress >> 8) & 0xff))
  LoadCode(0x6EF7)
  LoadCode(0x0E00 | (MemoryAddress & 0xff))
  LoadCode(0x6EF6)




def ReadMemoryPic18(MemoryAddress):
  LoadMemoryAddress(MemoryAddress)
  return ReadMemoryPic18Next()

def BulkErasePic18FXXX():
  print("Bulk Erase ",end='')
  LoadCode(0x8EA6)
  LoadCode(0x8CA6)
  LoadCode(0x86A6)
  LoadMemoryAddress(0x3C0004)
  LoadCommandWordPic18(C_PIC18_WRITE,0x0080)
  LoadCode(0)
  LoadCommandPic18(C_PIC18_NOP)
  sleep(0.015)
  LoadWordPic18(0)
  print("..... Done!")

def WriteDataPic18(DataToBurn):
  LoadCommandWordPic18(C_PIC18_START_PGM,DataToBurn)




def WriteAndWait():
  GPIO.setup(PIC_DATA,GPIO.OUT)
  GPIO.output(PIC_DATA, False)
  for loop in range(3):
     GPIO.output(PIC_CLK,True)
     #mydelay()
     GPIO.output(PIC_CLK,False)
     #mydelay()
  GPIO.output(PIC_CLK,True)
  sleep(0.001)
  GPIO.output(PIC_CLK,False)
  LoadWordPic18(0)


#validate search data in hex file dictionary. If it is not there assume blank (0xff)
def SearchByteValue(pic_data, AddressPointer):
  if pic_data.get(AddressPointer) != None:
    return pic_data.get(AddressPointer)
  else:
    return 0xff

def SearchWordValue(pic_data, AddressPointer):
  return (SearchByteValue(pic_data, AddressPointer) | (SearchByteValue(pic_data,AddressPointer+1) << 8))


def ProgramBurnPic18MultiPanel(pic_data, program_base, program_size,buffer_size):
  print("Writing Program",end='')
  NumberOfPanel = program_size / Pic18PanelSize 
  LoadCode(0x8EA6)
  LoadCode(0x8CA6)
  LoadCode(0x86A6)
  WaitFlag= False
  for CountIdx in range(0,Pic18PanelSize,buffer_size):
    LoadMemoryAddress(0x3C0006)
    LoadCommandWordPic18(C_PIC18_WRITE,0x0040)

    LoadCode(0x8EA6)
    LoadCode(0x9CA6)

    for PanelIdx in range(NumberOfPanel):
     AddressOffset = CountIdx + (PanelIdx * Pic18PanelSize)
     LoadMemoryAddress(AddressOffset)
     for DataWordIdx in range(0,buffer_size,2):
       if DataWordIdx == 6 :
         if PanelIdx == (NumberOfPanel -1):
           WaitFlag= True
           LoadCommandPic18(C_PIC18_START_PGM)
         else:
           LoadCommandPic18(C_PIC18_WRITE)
       else:
         LoadCommandPic18(C_PIC18_WRITE_INC_BY2)
       PAddress = AddressOffset + DataWordIdx  + program_base;
       LoadWordPic18(SearchWordValue(pic_data,PAddress))
       if WaitFlag:
         WriteAndWait()
         WaitFlag= False;
    if (CountIdx % 256)==0 :
      sys.stdout.write('.')
      sys.stdout.flush()
  print("Done!")


def ProgramErasePic18(program_size):
  print("row erase")
  #direct access to config memory
  LoadCode(0x8EA6)
  LoadCode(0x8CA6)
  LoadCode(0x86A6)

  #config device for multi panel
  LoadMemoryAddress(0x3C0006)
  LoadCommandWordPic18(C_PIC18_WRITE,0x40)


  for l in range(0,program_size,64):
    #direct access code memory mode
    LoadCode(0x8EA6)
    LoadCode(0x9CA6)
    LoadCode(0x88A6)

    LoadMemoryAddress(l)
    LoadCommandWordPic18(C_PIC18_START_PGM,0xffff)
    WriteAndWait()
    if (l % 1024)==0 :
      sys.stdout.write('.')
      sys.stdout.flush()
  print("Done!")

def ProgramBlankCheckPic18(program_size):
   print("Program code blank check",end='')
   LoadMemoryAddress(0)
   for l in range (program_size):
     Value = ReadMemoryPic18Next()
     if(Value != 0xff):
       print("*** CPU program at Address ", hex(l), " = ", hex(Value), " Failed!")
       return False
     if (l % 1024)==0 :
       sys.stdout.write('.')
       sys.stdout.flush()
   print("Passed!")
   return True

def MemoryCheckPic18(pic_data,memory_base,memory_size):
   LoadMemoryAddress(memory_base)
   for l in range (memory_size):
     Value = ReadMemoryPic18Next()
     TargetValue = SearchByteValue(pic_data,l + memory_base)
     if(Value != TargetValue):
       print("  **** Address ", hex(l), " write  ", hex(TargetValue), " read" , hex(Value))
       return False
     if (l % 1024)==0 :
       sys.stdout.write('.')
       sys.stdout.flush()
   return True


def ProgramCheckPic18(pic_data, program_base, program_size):
   print("Program check ",end='')
   if MemoryCheckPic18(pic_data,program_base, program_size):
     print("Passed!")
     return True
   return False





def  DataEepromBurnPic18(pic_data, DataEepromBase, DataEepromSize):
   print("Writing EEROM dat",end='')
   #direct access to data EEPROM
   LoadCode(0x9EA6)
   LoadCode(0x9CA6)
   for l in range(DataEepromSize):
     if (l % 32)==0 :
       sys.stdout.write('.')
       sys.stdout.flush()
     Value= SearchByteValue(pic_data, l + DataEepromBase)
     if Value == 0xff:
       continue
     #Set data EEPROM Address Pointer
     LoadEepromAddress(l)
     #Load the data to be written
     LoadCode(0x0e00 | Value)
     LoadCode(0x6EA8)
     #enable memory writes
     LoadCode(0x84A6)
     #perfom required sequence
     LoadCode(0x0E55)
     LoadCode(0x6EA7)
     LoadCode(0x0EAA)
     LoadCode(0x6EA7)
     #initiate write
     LoadCode(0x82A6)
     while True:
       #Poll WR bit,
       LoadCode(0x50A6)
       LoadCode(0x6EF5)
       LoadCommandPic18(C_PIC18_TABLAT)
       EECON1 = ReadDataPic18()
       if (EECON1 & 2) == 0:
         break
     LoadCode(0x94A6)
   print("Done!")


def DataEepromCheckPic18(pic_data, DataEepromBase, DataEepromSize):
   print("EEROM Data Check",end='')
   #Direct access to data EEPROM
   LoadCode(0x9EA6)
   LoadCode(0x9CA6)
   for l in range(DataEepromSize):
     if (l % 32)==0 :
       sys.stdout.write('.')
       sys.stdout.flush()
     Value= SearchByteValue(pic_data, l + DataEepromBase)
     #Set data EEPROM Address Pointer
     LoadEepromAddress(l)
     #Initiate A memory Read
     LoadCode(0x80A6)
     #Load data into the serial data
     LoadCode(0x50A8)
     LoadCode(0x6EF5)
     LoadCommandPic18(C_PIC18_TABLAT)
     RValue= ReadDataPic18()
     if Value != RValue :
       print("  *** EEROM  address ", hex(l), " write  ", hex(Value), " read" , hex(RValue))
       return False
   print("Done!")
   return True

def ReadEepromMemoryPic18(EeromAddress):
   #direct access to data EEPROM
   LoadCode(0x9EA6)
   LoadCode(0x9CA6)
   #Set data EEPROM Address pointer
   LoadEepromAddress(EeromAddress)
   #initiate a memory read
   LoadCode(0x80A6)
   #Load data into the serial data
   LoadCode(0x50A8)
   LoadCode(0x6EF5)
   LoadCommandPic18(C_PIC18_TABLAT)
   RValue = ReadDataPic18()
   return RValue



def IDLocationBurnPic18FXXX(pic_data,IDLocationBase,IDLocationSize):
   print("Writing ID",end='')
   #direct access config memory
   LoadCode(0x8EA6)
   LoadCode(0x8CA6)
   #configure single Panel
   LoadMemoryAddress(0x3C0006)
   LoadCommandWordPic18(C_PIC18_WRITE,0)
   #Direct access to code memory
   LoadCode(0x8EA6)
   LoadCode(0x9CA6)
   #Load Write buffer
   LoadMemoryAddress(0x200000)
   LoadCommandWordPic18(C_PIC18_WRITE_INC_BY2, SearchWordValue(pic_data,IDLocationBase))
   LoadCommandWordPic18(C_PIC18_WRITE_INC_BY2, SearchWordValue(pic_data,IDLocationBase+2))
   LoadCommandWordPic18(C_PIC18_WRITE_INC_BY2, SearchWordValue(pic_data,IDLocationBase+4))
   LoadCommandWordPic18(C_PIC18_START_PGM, SearchWordValue(pic_data,IDLocationBase+6))
   WriteAndWait()
   print(" ... Done!")
   return

def IDLocationCheckPic18(pic_data,ID_Base,ID_Size):
   print("ID Check ",end='')
   if MemoryCheckPic18(pic_data,ID_Base,ID_Size):
     print(" ... Passed!")
     return True
   return False



   return True

#create a config Mirror of 7 WORDS
ConfigMirror = [0xFFFF] * 7

def AnalyzeConfigPic18FXXX(pic_data, config_base):
   global ConfigMirror
   ConfigMask= [0x2700,0x0f0f,0x0100,0x0085,0xc00f,0xe00f,0x400f]
   #transfer Config1 .. Config7  and use mask
   for l in range(7):
     ConfigMirror[l] = SearchWordValue(pic_data, config_base + (l * 2)) & ConfigMask[l]
   #fix LVP in CONFIG4L  Force LVP
   ConfigMirror[3] = ConfigMirror[3] | 0x0004


def ConfigBurnPic18FXXX(pic_data, config_base):
   print("CONFIG Burn",end='')
   global ConfigMirror
   AnalyzeConfigPic18FXXX(pic_data,config_base)
   #burn all config but CONFIG6 last because of WRTC
   for l in range(5)+[6,5]:
     #direct access config memory
     LoadCode(0x8EA6)
     LoadCode(0x8CA6)
     #position program counter
     LoadCode(0xEF00)
     LoadCode(0xF800)
     #Set Table Pointer
     LoadMemoryAddress(config_base+(l*2))
     LoadCode(0x6EF6)
     LoadCommandWordPic18(C_PIC18_WRITE,ConfigMirror[l])
     WriteAndWait()
     LoadCode(0x2AF6)
     LoadCommandWordPic18(C_PIC18_WRITE,ConfigMirror[l])
     WriteAndWait()
   print(" ... Done!")


def ConfigCheckPic18FXXX(pic_data, config_base):
   print("Config Check ",end='')
   global ConfigMirror
   AnalyzeConfigPic18FXXX(pic_data,config_base)
   LoadMemoryAddress(config_base)
   for l in range (14):
     Value = ReadMemoryPic18Next()
     if (l & 1) == 0 :
        TargetValue = ConfigMirror[l / 2] & 0xff
     else:
        TargetValue = (ConfigMirror[l/2] >> 8) & 0xff
     if(Value != TargetValue):
       print("  **** Address ", hex(l), " write  ", hex(TargetValue), " read" , hex(Value))
       return False
     if (l % 1024)==0 :
       sys.stdout.write('.')
       sys.stdout.flush()
   print(" ... Passed!")
   return True




def ProgramDumpPic18(dump_base,dump_size):
   print("")
   print("----- MEMORY DUMP -----  BASE=", hex(dump_base))
   LoadCode(0)
   LoadMemoryAddress(dump_base)
   for l in range (dump_size):
     LoadMemoryAddress(dump_base+l)
     Value = ReadMemoryPic18Next()
     if (l % 32) == 0:
      print(format(l,'04x'), ":" ,end='')
     else:
       if (l % 4) == 0:
         print("-",end='')
     print(format(Value,'02X'),end='')
     if (l % 32) == 31:
      print(" ")

def DataEeromDumpPic18(data_size):
   print("")
   print("----- EEROM DATA -----")
   for l in range(data_size):
     Value = ReadEepromMemoryPic18(l)
     if (l % 32) == 0:
      print(format(l,'04x'), ":" ,end='')
     else:
       if (l % 4) == 0:
         print("-",end='')
     print(format(Value,'02X'),end='')
     if (l % 32) == 31:
      print(" ")




#///  GENERIC FUNCTION

def ConfigCheckPic18(pic_data, config_base, config_size):
  global PicFamilly
  if PicFamilly == PIC18FXXX:
    ConfigCheckPic18FXXX(pic_data, config_base)


def ConfigBurnPic18(pic_data, config_base, config_size):
  global PicFamilly
  if PicFamilly == PIC18FXXX:
    ConfigBurnPic18FXXX(pic_data,config_base)


def IDLocationBurnPic18(pic_data,IDLocationBase,IDLocationSize):
  global PicFamilly
  if PicFamilly == PIC18FXXX:
    IDLocationBurnPic18FXXX(pic_data,IDLocationBase,IDLocationSize)
#  elif PicFamilly == PIC18FXXXX:
#  else:



def  BulkErasePic18():
  global PicFamilly
  if PicFamilly == PIC18FXXX:
    BulkErasePic18FXXX()
#  elif PicFamilly == PIC18FXXXX:
#  else:



def   ProgramBurnPic18(PicData,ProgramBase,ProgramSize):
  global PicFamilly
  if PicFamilly == PIC18FXXX:
    ProgramBurnPic18MultiPanel(PicData,ProgramBase,ProgramSize,8)
#  elif PicFamilly == PIC18FXXXX:
#    ProgramBurnPic18F2580:
#  else:


#=============  main ==========

if __name__ == '__main__':
  if len(sys.argv) is 2:
    HexFile = sys.argv[1]
  elif len(sys.argv) is 1:
    HexFile = ''
  else:
    print('Usage: %s file.hex' % sys.argv[0])
    quit()


## load hex file if it exist
FileData =  IntelHex()
if len(HexFile) > 0 :
   try:
     FileData.loadhex(HexFile)
   except IOError:
     print('Error in file "', HexFile, '"')
     quit()

PicData = FileData.todict()
print('File "', HexFile, '" loaded')



GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)


GPIO.setup(PIC_PGM,GPIO.OUT)
GPIO.setup(PIC_MCLR,GPIO.OUT)
GPIO.setup(PIC_CLK,GPIO.OUT)
GPIO.setup(PIC_DATA,GPIO.IN)

Set_LVP_PIC18()
CpuRevision = ReadMemoryPic18(0x3ffffe)
CpuId = ReadMemoryPic18Next()
CpuId = (CpuId << 8 ) | (CpuRevision & 0xE0)
CpuRevision = CpuRevision & 0x1f

print("Cpu Id =" , hex(CpuId))
print("Revision=" , hex(CpuRevision))

DataEepromBase = 0xf00000
DataEepromSize = 256
ProgramBase = 0
ProgramSize = 32768
IDLocationBase = 0x200000
IDLocationSize = 8
ConfigBase = 0x300000
ConfigSize = 14
WriteBufferSize = 8
if CpuId != 0x840 :
   print(" not a pic18f258")
   quit()

PicFamilly = PIC18FXXX


BulkErasePic18()
if ProgramBlankCheckPic18(ProgramSize):
  ProgramBurnPic18(PicData,ProgramBase,ProgramSize)
  if ProgramCheckPic18(PicData,ProgramBase,ProgramSize):
    DataEepromBurnPic18(PicData, DataEepromBase, DataEepromSize)
    if DataEepromCheckPic18(PicData, DataEepromBase, DataEepromSize):
      IDLocationBurnPic18(PicData,IDLocationBase,IDLocationSize)
      if IDLocationCheckPic18(PicData,IDLocationBase,IDLocationSize):
        ConfigBurnPic18(PicData, ConfigBase, ConfigSize)
        if ConfigCheckPic18(PicData, ConfigBase, ConfigSize):
           print("Program verification passed!")


#debug dump function
#ProgramDumpPic18(0,0x100)
#DataEeromDumpPic18(256)

#Code DUMP
#ProgramDumpPic18(ProgramBase+ offset, size)


#CONFIG DUMP
#ProgramDumpPic18(ConfigBase,ConfigSize)

Release_LVP_PIC18()







