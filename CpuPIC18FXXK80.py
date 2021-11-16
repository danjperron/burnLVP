#!/usr/bin/env python3

################################
#
#  Class to program PIC18FXXK80 family
#
#
#  class PIC18FXXK80
#  inherit from class PIC18F
#
# N.B. line PGM is not needed! Use the MCLR with magic number
#
# programmer : Daniel Perron
# Date       : Sept 27, 2013
# Version    : 2.0
#
# Enhanced version of  burnLVP  for pic18F...
#
# source code:  https://github.com/danjperron/A2D_PIC_RPI
#
#
#

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



import burnGPIO as IO
from time import sleep
import sys, termios, atexit
from intelhex import IntelHex
from select import select
from  CpuPIC18F import PIC18F

class PIC18FXXK80(PIC18F):

  WriteBufferSize =64
  EraseBufferSize =64
  #cpu List dict.  CpuId  [Name , IdMask, Revision Mask, Block Size, Block Count, Program Size, WriteBuffer]	

  DataSize = 1024
  ListName = 0
  ListProgramSize = 1

  CpuList = {
               # ID         Name        Code Size 
		0x60E0 : ['PIC18F66K80' , 0x10000 ],
		0x6100 : ['PIC18F46K80' , 0x10000 ],
		0x6120 : ['PIC18F26K80' , 0x10000 ],
		0x6140 : ['PIC18F65K80' , 0x8000  ],
		0x6160 : ['PIC18F45K80' , 0x8000  ],
		0x6180 : ['PIC18F25K80' , 0x8000  ],
		0x61C0 : ['PIC18LF66K80' , 0x10000 ],
		0x61E0 : ['PIC18LF46K80' , 0x10000 ],
		0x6200 : ['PIC18LF26K80' , 0x10000 ],
		0x6220 : ['PIC18LF65K80' , 0x8000  ],
		0x6240 : ['PIC18LF45K80' , 0x8000  ],
		0x6260 : ['PIC18LF25K80' , 0x8000  ]
             }

  PicFamily = 'PIC18FXXK80'


  def SendMagic(self):
    magic = 0x4d434850

    #MSB FIRST
    IO.GPIO.setup(IO.PIC_DATA, IO.GPIO.OUT)

    for loop in range(32):
      f = (magic & 0x80000000) == 0x80000000
#      if f:
#        print 1,
#      else:
#        print 0,
#      IO.GPIO.output(IO.PIC_DATA, (magic & 0x80000000) == 0x80000000)
      IO.GPIO.output(IO.PIC_DATA, f)
      IO.GPIO.output(IO.PIC_CLK, True)
      IO.GPIO.output(IO.PIC_CLK, False)
      magic = magic << 1

  def Set_LVP(self):
     #put MCLR HIGH
     IO.GPIO.output(IO.PIC_CLK, False)
     IO.GPIO.setup(IO.PIC_DATA, IO.GPIO.OUT)
     IO.GPIO.output(IO.PIC_DATA, False)
     IO.GPIO.output(IO.PIC_MCLR, True)
     sleep(0.1)
     #put MCLR LOW
     IO.GPIO.output(IO.PIC_MCLR, False)
     sleep(0.001)
     self.SendMagic()
     sleep(0.001)
     #put MCLR HIGH
     IO.GPIO.output(IO.PIC_MCLR, True)
     sleep(0.1)
     _byte1 = self.ReadMemory(0x3ffffe)
     _byte2 = self.ReadMemoryNext()
     if (_byte1 != 255) or ( _byte2 != 255):
       print("IdTag ", hex(_byte1), ",", hex(_byte2))

  def Release_LVP(self):
     #just keep it on reset
     IO.GPIO.output(IO.PIC_MCLR, True)
     sleep(0.001)
     IO.GPIO.output(IO.PIC_MCLR, False)



  def BulkErase(self):
    print("Bulk Erase ",end='')
    #erase BLOCK 
    for l in range(4):
      self.LoadMemoryAddress(0x3C0004)
      self.LoadCommandWord(self.C_PIC18_WRITE,0x404)
      self.LoadMemoryAddress(0x3C0005)
      Value = 1 << l
      Value = Value  | (Value << 8)
      self.LoadCommandWord(self.C_PIC18_WRITE,Value)
      self.LoadMemoryAddress(0x3C0006)
      self.LoadCommandWord(self.C_PIC18_WRITE,0x8080)
      self.LoadCode(0)
      self.LoadCommand(self.C_PIC18_NOP)
      #wait 6 ms
      sleep(0.006)
      self.LoadWord(0)
    #erase boot block
    self.LoadMemoryAddress(0x3C0004)
    self.LoadCommandWord(self.C_PIC18_WRITE,0x505)
    self.LoadMemoryAddress(0x3C0005)
    self.LoadCommandWord(self.C_PIC18_WRITE,0x0)
    self.LoadMemoryAddress(0x3C0006)
    self.LoadCommandWord(self.C_PIC18_WRITE,0x8080)
    self.LoadCode(0)
    self.LoadCommand(self.C_PIC18_NOP)
    #wait 6 ms
    sleep(0.006)
    self.LoadWord(0)
    #erase config.Fuses
    self.LoadMemoryAddress(0x3C0004)
    self.LoadCommandWord(self.C_PIC18_WRITE,0x0202)
    self.LoadMemoryAddress(0x3C0005)
    self.LoadCommandWord(self.C_PIC18_WRITE,0x0000)
    self.LoadMemoryAddress(0x3C0006)
    self.LoadCommandWord(self.C_PIC18_WRITE,0x8080)
    self.LoadCode(0)
    self.LoadCommand(self.C_PIC18_NOP)
    #wait 6 ms
    sleep(0.006)
    self.LoadWord(0)
    #erase eerom data
    self.LoadMemoryAddress(0x3C0004)
    self.LoadCommandWord(self.C_PIC18_WRITE,0x0404)
    self.LoadMemoryAddress(0x3C0005)
    self.LoadCommandWord(self.C_PIC18_WRITE,0x0000)
    self.LoadMemoryAddress(0x3C0006)
    self.LoadCommandWord(self.C_PIC18_WRITE,0x8080)
    self.LoadCode(0)
    self.LoadCommand(self.C_PIC18_NOP)
    sleep(0.006)
    self.LoadWord(0)
    print("..... Done!")



  def ProgramBurn(self, pic_data):
    print("Writing Program BufferSize=",end='')
    print(self.WriteBufferSize,end='')
    #Direct access to code memory
    self.LoadCode(0x8E7F)
    self.LoadCode(0x9C7F)
    self.LoadCode(0x847F)


    #create a buffer to hold program code
    WordCount = self.WriteBufferSize/2
    wbuffer = [0xffff] * WordCount

    #ok load until all code is written

    for l in range(0,self.ProgramSize, self.WriteBufferSize):

      BlankFlag= True
      #get all buffer and check if they are all blank
      for i in range(WordCount):
        wbuffer[i] = self.SearchWordValue(pic_data, l+(i * 2)+self.ProgramBase)
        if wbuffer[i] != 0xffff:
          BlankFlag= False

      #if they are all blank just skip it
      if BlankFlag:
        continue

      #ok let's write the buffer
      self.LoadMemoryAddress(l)
      for i in range(WordCount-1):
        self.LoadCommandWord(self.C_PIC18_WRITE_INC_BY2,wbuffer[i])
      self.LoadCommandWord(self.C_PIC18_START_PGM,wbuffer[WordCount-1])

      #and wait
      self.WriteAndWait()
      if (l % 1024) == 0:
        sys.stdout.write('.')
        sys.stdout.flush()
    #disable write
    self.LoadCode(0x947F)
    print("Done!")


  def  DataBurn(self,pic_data):
    print("Writing EEPROM data[",self.DataSize,"]",end="")
    #direct access to data EEPROM
    self.LoadCode(0x9E7F)
    self.LoadCode(0x9C7F)
    for l in range(self.DataSize):
      if (l % 32)==0 :
        sys.stdout.write('.')
        sys.stdout.flush()
      Value= self.SearchByteValue(pic_data, l + self.DataBase)
      if Value == 0xff:
        continue
      #Set data EEPROM Address Pointer
      self.LoadEepromAddress(l)
      #Load the data to be written
      self.LoadCode(0x0e00 | Value)
      self.LoadCode(0x6E73)
      #enable memory writes
      self.LoadCode(0x847F)
      #Initiate write
      self.LoadCode(0x827F)
      #Poll WR bit until bit is clear
      while True:
        #Poll WR bit,
        self.LoadCode(0x507F)
        self.LoadCode(0x6EF5)
        self.LoadCommand(self.C_PIC18_TABLAT)
        EECON1 = self.ReadData()
        if (EECON1 & 2) == 0:
          break
# sleep maybe needed if using python compiler
#      sleep(0.0001)

      #disable write
      self.LoadCode(0x947F)
    print("Done!")





  def IDBurn(self,pic_data):
    print("Writing ID",end='')
    #direct access config memory
    self.LoadCode(0x8E7F)
    self.LoadCode(0x9C7F)
    #Load Write buffer
    self.LoadMemoryAddress(0x200000)
    self.LoadCommandWord(self.C_PIC18_WRITE_INC_BY2, self.SearchWordValue(pic_data,self.IDBase))
    self.LoadCommandWord(self.C_PIC18_WRITE_INC_BY2, self.SearchWordValue(pic_data,self.IDBase+2))
    self.LoadCommandWord(self.C_PIC18_WRITE_INC_BY2, self.SearchWordValue(pic_data,self.IDBase+4))
    self.LoadCommandWord(self.C_PIC18_START_PGM, self.SearchWordValue(pic_data,self.IDBase+6))
    self.WriteConfig()
    print(" ... Done!")
    return


  ConfigMask = [0x5d, 0xdf, 0x7F, 0x7f, 0, 0x8f, 0x91,0, 0x0f, 0xC0, 0x0F, 0xE0, 0x0f, 0x40]

  def WriteConfig(self):
    IO.GPIO.setup(IO.PIC_DATA, IO.GPIO.OUT)
    IO.GPIO.output(IO.PIC_DATA, False)
    pass
    for loop in range(3):
       IO.GPIO.output(IO.PIC_CLK, True)
       pass
       IO.GPIO.output(IO.PIC_CLK, False)
       pass
    IO.GPIO.output(IO.PIC_CLK, True)
    sleep(0.01)
    IO.GPIO.output(IO.PIC_CLK, False)
    pass
    self.LoadWord(0)


  def ConfigBurn(self,pic_data):
    print("CONFIG Burn",end='')
    #direct access config memory
    self.LoadCode(0x8E7F)
    self.LoadCode(0x8C7F)

    #burn all config but CONFIG6 last because of WRTC
    for l in range(11)+[12,13,11]:
      #if config is 30004h or 30007h skip it
      if  (l == 4) or (l==7) :
        continue
      #get Config Target Value
      TargetValue = pic_data.get(self.ConfigBase +l)
      if TargetValue == None:
        continue
      #use mask to disable unwanted bit
      TargetValue = TargetValue & self.ConfigMask[l]
      #put MSB and LSB the same
      TargetValue = TargetValue | (TargetValue << 8)
      self.LoadMemoryAddress(self.ConfigBase+ l)
      self.LoadCommandWord(self.C_PIC18_START_PGM,TargetValue)
      self.WriteConfig()
    self.LoadCode(0x947F)
    print(" ... Done!")



  def ConfigCheck(self,pic_data):
    print("Config Check ",end='')
    self.LoadMemoryAddress(self.ConfigBase)
    for l in range (14):
      Value = self.ReadMemoryNext()
      #if config is 30004h or 30007h skip it
      if  (l == 4) or (l==7) :
        continue
      TargetValue = pic_data.get(self.ConfigBase +l)
      if TargetValue == None:
        continue
      #use mask to disable unwanted bit
      TargetValue = TargetValue & self.ConfigMask[l]
      Value = Value & self.ConfigMask[l]
      if(Value != TargetValue):
        print("  **** Address ", hex(l), " write  ", hex(TargetValue), " read" , hex(Value))
        return False
      if (l % 1024)==0 :
        sys.stdout.write('.')
        sys.stdout.flush()
    print(" ... Passed!")
    return True


  def LoadEepromAddress(self,EepromAddress):
    self.LoadCode(0x0E00 | ((EepromAddress >>  8)  & 0xff))
    self.LoadCode(0x6E74)
    self.LoadCode(0x0E00 | (EepromAddress & 0xff))
    self.LoadCode(0x6E75)

  def DataBlankCheck(self):
    print("EEPROM DATA[",self.DataSize,"] Blank Check ",end='')
    #Direct access to data EEPROM
    self.LoadCode(0x9E7F)
    self.LoadCode(0x9C7F)
    for l in range(self.DataSize):
      if (l % 32)==0 :
        sys.stdout.write('.')
        sys.stdout.flush()
      #Set data EEPROM Address Pointer
      self.LoadEepromAddress(l)
      #Initiate A memory Read
      self.LoadCode(0x807F)
      #Load data into the serial data
      self.LoadCode(0x5073)
      self.LoadCode(0x6EF5)
      self.LoadCode(0)
      self.LoadCommand(self.C_PIC18_TABLAT)
      RValue= self.ReadData()
      if RValue != 0xff :
        print("  *** EEPROM DATA  address ", hex(l), " not blank!  read" , hex(RValue))
        return False
    print("Done!")
    return True

  def DataCheck(self,pic_data):
    print("EEPROM DATA[",self.DataSize,"]  Check ",end='')
    #Direct access to data EEPROM
    self.LoadCode(0x9E7F)
    self.LoadCode(0x9C7F)
    for l in range(self.DataSize):
      if (l % 32)==0 :
        sys.stdout.write('.')
        sys.stdout.flush()
      Value = self.SearchByteValue(pic_data, l + self.DataBase)
      #Set data EEPROM Address Pointer
      self.LoadEepromAddress(l)
      #Initiate A memory Read
      self.LoadCode(0x807F)
      #Load data into the serial data
      self.LoadCode(0x5073)
      self.LoadCode(0x6EF5)
      self.LoadCode(0)
      self.LoadCommand(self.C_PIC18_TABLAT)
      RValue= self.ReadData()
      if Value != RValue :
        print("  *** EEROM  address ", hex(l), " write  ", hex(Value), " read" , hex(RValue))
        return False
    print("Done!")
    return True



  def FindCpu(self, Id):
    _cpuInfo =self.CpuList.get(Id & 0xFFE0)
    if _cpuInfo != None:
      self.ProgramSize = _cpuInfo[self.ListProgramSize]
      self.CpuId = Id & 0xFFE0
      self.CpuRevision = Id &0x1F
      return _cpuInfo 
    return  None




