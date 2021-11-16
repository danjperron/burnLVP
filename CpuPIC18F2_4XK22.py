#!/usr/bin/env python3

################################
#
#  Class to program PIC18F2XK22/PIC18F4XK22 family
#
#
#  class PIC18F2_4XK22
#  inherit from class PIC18F
#
# N.B. line PGM is not needed! Use the MCLR with magic number
#
# programmer : Pascal Sandrez adapted from Daniel Perron code
# Date       : Dec 18, 2014
# Version    : 1.0
#


#////////////////////////////////////  MIT LICENSE ///////////////////////////////////
#	The MIT License (MIT)
#
#	Copyright (c) 2014 Pascal Sandrez, Daniel Perron
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

class PIC18F2_4XK22(PIC18F):

  EraseBufferSize = 64
  
  #cpu List dict.  CpuId  [Name , Program Size, Data Size, Write buffer size]
  ListName = 0
  ListProgramSize = 1
  ListDataSize = 2
  ListWriteBufferSize = 3

  CpuList = {
       # ID         Name       Code Size Data Size  Write buffer size
      0x5500 : ['PIC18F45K22' , 0x8000  ,   256     , 32 ],
      0x5520 : ['PIC18LF45K22', 0x8000  ,   256     , 32 ],
      0x5540 : ['PIC18F25K22' , 0x8000  ,   256     , 32 ],
      0x5560 : ['PIC18LF25K22', 0x8000  ,   256     , 32 ],
      0x5740 : ['PIC18F23K22' , 0x2000  ,   256     , 32 ],
      0x5760 : ['PIC18LF23K22', 0x2000  ,   256     , 32 ],
      0x5640 : ['PIC18F24K22' , 0x4000  ,   256     , 32 ],
      0x5660 : ['PIC18LF24K22', 0x4000  ,   256     , 32 ],
      0x5440 : ['PIC18F26K22' , 0x10000 ,   1024    , 64 ],
      0x5460 : ['PIC18LF26K22', 0x10000 ,   1024    , 64 ],
      0x5700 : ['PIC18F43K22' , 0x2000  ,   256     , 32 ],
      0x5720 : ['PIC18LF43K22', 0x2000  ,   256     , 32 ],
      0x5600 : ['PIC18F44K22' , 0x4000  ,   256     , 32 ],
      0x5620 : ['PIC18LF44K22', 0x4000  ,   256     , 32 ],
      0x5400 : ['PIC18F46K22' , 0x10000 ,   1024    , 64 ],
      0x5420 : ['PIC18LF46K22', 0x10000 ,   1024    , 64 ]
             }

  PicFamily = 'PIC18F2XK22/PIC18F4XK22'

  def SendMagic(self):
    magic = 0x4d434850
    IO.GPIO.setup(IO.PIC_DATA, IO.GPIO.OUT, initial=IO.GPIO.LOW)
    #MSB FIRST
    for loop in range(32):
      f = (magic & 0x80000000) == 0x80000000
      IO.GPIO.output(IO.PIC_DATA, f)
      IO.GPIO.output(IO.PIC_CLK, True)
      IO.GPIO.output(IO.PIC_CLK, False)
      magic = magic << 1


  def Set_LVP(self):
     #put MCLR HIGH
     IO.GPIO.output(IO.PIC_CLK, False)
     IO.GPIO.setup(IO.PIC_DATA, IO.GPIO.OUT,initial=IO.GPIO.LOW)
     IO.GPIO.setup(IO.PIC_MCLR, IO.GPIO.OUT,initial=IO.GPIO.LOW)
     IO.GPIO.output(IO.PIC_MCLR, True)
     sleep(0.1)
     #put MCLR LOW
     IO.GPIO.output(IO.PIC_MCLR, False)
     sleep(0.002) # P18 = 1ms min
     self.SendMagic()
     sleep(0.001) # P20 = 40ns min
     #put MCLR HIGH
     IO.GPIO.output(IO.PIC_MCLR, True)
     sleep(0.001) # P15 = 400us min
     _byte1 = self.ReadMemory(0x3ffffe)
     _byte2 = self.ReadMemoryNext()
     print("IdTag ", hex(_byte1), ",", hex(_byte2))


  def Release_LVP(self):
     #just keep it on reset
     IO.GPIO.output(IO.PIC_MCLR, True)
     sleep(0.001)
     IO.GPIO.output(IO.PIC_MCLR, False)


  def BulkErase(self):
    print("Bulk Erase ",end='')
    #erase full chip
    self.LoadMemoryAddress(0x3C0005)
    self.LoadCommandWord(self.C_PIC18_WRITE,0x0f0f)
    self.LoadMemoryAddress(0x3C0004)
    self.LoadCommandWord(self.C_PIC18_WRITE,0x8f8f)
    self.LoadCode(0)
    self.LoadCommand(self.C_PIC18_NOP)
    sleep(0.016) # P10 (200us) + P11 (15ms)
    self.LoadWord(0)
    print("..... Done!")


  def ProgramBurn(self, pic_data):
    print("Writing Program BufferSize = ",self.WriteBufferSize,end='')
    #Direct access to code memory
    self.LoadCode(0x8EA6)
    self.LoadCode(0x9CA6)
    self.LoadCode(0x84A6)

    #create a buffer to hold program code
    WordCount = self.WriteBufferSize/2
    wbuffer = [0xffff] * WordCount
    
    #ok load until all code is written

    for l in range(0,self.ProgramSize, self.WriteBufferSize):
      BlankFlag = True
      #get all buffer and check if they are all blank
      for i in range(WordCount):
        wbuffer[i] = self.SearchWordValue(pic_data, l+(i * 2)+self.ProgramBase)
        if wbuffer[i] != 0xffff:
          BlankFlag = False

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
    self.LoadCode(0x94A6) 
    print("Done!")


  def DataBurn(self,pic_data):
    print("Writing EEPROM data [",self.DataSize,"]",end='')
    #direct access to data EEPROM
    self.LoadCode(0x9EA6)
    self.LoadCode(0x9CA6)
    for l in range(self.DataSize):
      if (l % 32)==0 :
        sys.stdout.write('.')
        sys.stdout.flush()
      Value = self.SearchByteValue(pic_data, l + self.DataBase)
      if Value == 0xff:
        continue
      #Set data EEPROM Address Pointer
      self.LoadEepromAddress(l)
      #Load the data to be written
      self.LoadCode(0x0E00 | Value)
      self.LoadCode(0x6EA8)
      #enable memory writes
      self.LoadCode(0x84A6) 
      #Initiate write
      self.LoadCode(0x82A6)
      self.LoadCode(0)
      self.LoadCode(0)
      #Poll WR bit until bit is clear
      while True:
        #Poll WR bit,
        self.LoadCode(0x50A6)
        self.LoadCode(0x6EF5)
        self.LoadCode(0)
        self.LoadCommand(self.C_PIC18_TABLAT)
        EECON1 = self.ReadData()
        if (EECON1 & 2) == 0:
          break
# sleep maybe needed if using python compiler
#      sleep(0.0001)
      #disable write
      self.LoadCode(0x94A6)
    print("Done!")


  def IDBurn(self,pic_data):
    print("Writing ID",end='')
    #direct access config memory
    self.LoadCode(0x8EA6)
    self.LoadCode(0x9CA6)
    self.LoadCode(0x84A6)
    #Load Write buffer
    self.LoadMemoryAddress(0x200000)
    self.LoadCommandWord(self.C_PIC18_WRITE_INC_BY2, self.SearchWordValue(pic_data,self.IDBase))
    self.LoadCommandWord(self.C_PIC18_WRITE_INC_BY2, self.SearchWordValue(pic_data,self.IDBase+2))
    self.LoadCommandWord(self.C_PIC18_WRITE_INC_BY2, self.SearchWordValue(pic_data,self.IDBase+4))
    self.LoadCommandWord(self.C_PIC18_START_PGM, self.SearchWordValue(pic_data,self.IDBase+6))
    self.WriteConfig()   
    print(" ... Done!")
    return  

              # 0     1     2     3     4     5     6     7     8     9     A     B     C     D
  ConfigMask = [0x00, 0x25, 0x1F, 0x3F, 0x00, 0xBF, 0x85, 0x00, 0x0F, 0xC0, 0x0F, 0xE0, 0x0F, 0x40]

  def WriteConfig(self):
    IO.GPIO.setup(IO.PIC_DATA, IO.GPIO.OUT, initial=IO.GPIO.LOW)
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
    print("Config Burn",end='')
    #direct access config memory
    self.LoadCode(0x8EA6)
    self.LoadCode(0x8CA6)
    self.LoadCode(0x84A6)

    #burn all config but CONFIG6 last because of WRTC
    for l in range(11)+[12,13,11]:
      #if config is 300000h or 300004h or 300007h skip it
      if  (l == 0) or (l == 4) or (l == 7) :
        continue
      #get Config Target Value
      TargetValue = pic_data.get(self.ConfigBase + l)
      if TargetValue == None:
        continue
      #use mask to disable unwanted bit
      TargetValue = TargetValue & self.ConfigMask[l]
      #put MSB and LSB the same
      TargetValue = TargetValue | (TargetValue << 8)
      self.LoadMemoryAddress(self.ConfigBase + l)
      self.LoadCommandWord(self.C_PIC18_START_PGM,TargetValue)
      self.WriteConfig()
    self.LoadCode(0x947F)
    print(" ... Done!")


  def ConfigCheck(self,pic_data):
    print("Config Check ",end='')
    self.LoadMemoryAddress(self.ConfigBase)
    for l in range (14):
      Value = self.ReadMemoryNext()
      #if config is 300000h or 300004h or 300007h skip it
      if  (l == 0) or (l == 4) or (l == 7) :
        continue
      TargetValue = pic_data.get(self.ConfigBase +l)
      if TargetValue == None:
        continue
      #use mask to disable unwanted bit
      TargetValue = TargetValue & self.ConfigMask[l]
      Value = Value & self.ConfigMask[l]
      if(Value != TargetValue):
        print("  **** Config check error address ", hex(l), " write ", hex(TargetValue), " read" , hex(Value))
        return False
      if (l % 1024)==0 :
        sys.stdout.write('.')
        sys.stdout.flush()
    print(" ... Passed!")
    return True


  def LoadEepromAddress(self,EepromAddress):
    self.LoadCode(0x0E00 | ((EepromAddress >>  8) & 0xff))
    self.LoadCode(0x6EA9)
    self.LoadCode(0x0E00 | (EepromAddress & 0xff))
    self.LoadCode(0x6EAA)


  def DataBlankCheck(self):
    print("EEPROM Data [",self.DataSize,"] Blank Check ",end='')
    #Direct access to data EEPROM
    self.LoadCode(0x9EA6)
    self.LoadCode(0x9CA6)
    for l in range(self.DataSize):
      if (l % 32)==0 :
        sys.stdout.write('.')
        sys.stdout.flush()
      #Set data EEPROM Address Pointer
      self.LoadEepromAddress(l)
      #Initiate A memory Read
      self.LoadCode(0x80A6)
      #Load data into the serial data
      self.LoadCode(0x50A8)
      self.LoadCode(0x6EF5)
      self.LoadCode(0)
      self.LoadCommand(self.C_PIC18_TABLAT)
      RValue = self.ReadData()
      if RValue != 0xff :
        print("  *** EEPROM Data blank check error address ", hex(l), " not blank! read" , hex(RValue))
        return False
    print("Done!")
    return True


  def DataCheck(self,pic_data):
    print("EEPROM DATA [",self.DataSize,"] Check ",end='')
    #Direct access to data EEPROM
    self.LoadCode(0x9EA6)
    self.LoadCode(0x9CA6)
    for l in range(self.DataSize):
      if (l % 32)==0 :
        sys.stdout.write('.')
        sys.stdout.flush()
      Value = self.SearchByteValue(pic_data, l + self.DataBase)
      #Set data EEPROM Address Pointer
      self.LoadEepromAddress(l)
      #Initiate A memory Read
      self.LoadCode(0x80A6)
      #Load data into the serial data
      self.LoadCode(0x50A8)
      self.LoadCode(0x6EF5)
      self.LoadCode(0)
      self.LoadCommand(self.C_PIC18_TABLAT)
      RValue = self.ReadData()
      if Value != RValue :
        print("  *** EEPROM DATA check error address ", hex(l), " write ", hex(Value), " read" , hex(RValue))
        return False
    print("Done!")
    return True


  def FindCpu(self, Id):
    _cpuInfo = self.CpuList.get(Id & 0xFFE0)
    if _cpuInfo != None:
      self.WriteBufferSize = _cpuInfo[self.ListWriteBufferSize]
      self.ProgramSize = _cpuInfo[self.ListProgramSize]
      self.DataSize = _cpuInfo[self.ListDataSize]
      self.CpuId = Id & 0xFFE0
      self.CpuRevision = Id &0x1F
      return _cpuInfo 
    return  None

