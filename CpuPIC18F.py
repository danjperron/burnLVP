#!/usr/bin/env python

################################
#
# CpuPIC18F  
#
#
# Program to burn pic18F...using LVP mode with a Rasberry Pi
#
#
# programmer : Daniel Perron
# Date       : Sept 25, 2013
# Version    : 0.001
#
# main class for PIC18F familly
#
# source code:  https://github.com/danjperron/burnLVP
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


#inport GPIO interface
from burnGPIO import *

from time import sleep
import sys, termios, atexit
from intelhex import IntelHex
from select import select   






class PIC18F:


  #Cpu Identification  
  #CpuTAg is 2 bytes info which could be split to get Cpu Id and Revision  
  CpuTag=0
  CpuId=0
  CpuRevision=0


  PanelSize=0

  DataBase = 0xf00000
  DataSize = 256
  ProgramBase = 0
  ProgramSize = 32768
  IDBase = 0x200000
  IDSize = 8
  ConfigBase = 0x300000
  ConfigSize = 14
  WriteBufferSize = 8
  PicFamily= "PIC18F..."

   


  # command definition
  C_PIC18_NOP	        = 0b0000
  C_PIC18_INSTRUCTION   = 0b0000
  C_PIC18_TABLAT        = 0b0010
  C_PIC18_READ          = 0b1000
  C_PIC18_READ_INC      = 0b1001
  C_PIC18_READ_DEC      = 0b1010
  C_PIC18_READ_PRE_INC  = 0b1011
  C_PIC18_WRITE         = 0b1100
  C_PIC18_WRITE_INC_BY2 = 0b1101
  C_PIC18_WRITE_DEC_BY2 = 0b1110
  C_PIC18_START_PGM     = 0b1111

  def __init__(self):
    #put default value
    self.PanelSize=8192
    self.CodeSize=8192
    self.EeromSize=256


  def Set_LVP(self):
   #held MCLR LOW
   setMCLRState( False)

   #hdel PIC_CLK & PIC_DATA & PIC_PGM low
   setClockState( False)
   setDataModeWrite()
   setDataState( False)
   setPGMState( False)

   sleep(0.01)
   #set PGM High
   setPGMState( True)
   sleep(0.01)
   #Set MCLR High
   setMCLRState( True)
   sleep(0.01)


  def Release_LVP(self):
   #set PGM Low
   setPGMState( False)
   sleep(0.1)

   #held MCLR LOW
   setMCLRState( False)

   #keep in reset mode


  def LoadWord(self, Value):
   setDataModeWrite()
   for loop in range(16):
     setDataState( (Value & 1) ==1 )
     setClockState( True)
     clockInterval()
     setClockState( False)
     clockInterval()
     Value = Value >> 1;

  
  def ReadData(self):
   setDataModeRead()
   # 8 clock cycles to let data be fetched into registers
   for loop in range(8):
    setClockState( True)
    clockInterval()
    setClockState( False)
    clockInterval()
   Value = 0

   # 8 Read cycles to read from register to data line
   for loop in range(8):
    setClockState( True)
    clockInterval()
    if getDataState():
        Value =  Value | (1 << loop)
    setClockState( False)
    clockInterval()
   return Value

  def LoadCommand(self,Value):
   setDataModeWrite()
   for loop in range(4):
     setDataState( (Value & 1) == 1)
     clockInterval() # MSM pass
     setClockState( True)
     clockInterval()
     setClockState( False)
     clockInterval()
     Value = Value >> 1;

  def LoadCommandWord(self,CommandValue,WordValue):
    self.LoadCommand(CommandValue)
    self.LoadWord(WordValue)


  def LoadCode(self,Instruction):
    self.LoadCommandWord(self.C_PIC18_INSTRUCTION,Instruction)


  def ReadMemoryNext(self):
    self.LoadCommand(self.C_PIC18_READ_INC)
    return self.ReadData()



  def LoadEepromAddress(self,EepromAddress):
    self.LoadCode(0x0E00 | ((EepromAddress >>  8)  & 0xff))
    self.LoadCode(0x6EAA)
    self.LoadCode(0x0E00 | (EepromAddress & 0xff))
    self.LoadCode(0x6EA9)
  

  def LoadMemoryAddress(self,MemoryAddress):
    self.LoadCode(0x0E00 | ((MemoryAddress >> 16) & 0xff))
    self.LoadCode(0x6EF8)
    self.LoadCode(0x0E00 | ((MemoryAddress >> 8) & 0xff))
    self.LoadCode(0x6EF7)
    self.LoadCode(0x0E00 | (MemoryAddress & 0xff))
    self.LoadCode(0x6EF6)
 



  def ReadMemory(self,MemoryAddress):
    self.LoadMemoryAddress(MemoryAddress)
    return self.ReadMemoryNext()


  def WriteAndWait(self):
    setDataModeWrite()
    setDataState( False)
    for loop in range(3):
       setClockState( True)
       clockInterval()
       setClockState( False)
       clockInterval()
    setClockState( True)
    clockInterval()
    setClockState( False)
    clockInterval()
    self.LoadWord(0)


  #validate search data in hex file dictionary. If it is not there assume blank (0xff)
  def SearchByteValue(self,pic_data, AddressPointer):
    if pic_data.get(AddressPointer) != None:
      return pic_data.get(AddressPointer)
    else:
      return 0xff

  def SearchWordValue(self,pic_data, AddressPointer):
    return (self.SearchByteValue(pic_data, AddressPointer) | (self.SearchByteValue(pic_data,AddressPointer+1) << 8))



  def ScanCpuTag(self):
   print "check ", self.PicFamily, "..."
   self.Set_LVP()
   _Byte1 = self.ReadMemory(0x3ffffe)
   _Byte2 = self.ReadMemoryNext()
   self.CpuTag = (_Byte2 << 8 ) | _Byte1
   self.CpuId = self.CpuTag & 0xFFE0
   self.CpuRevision = _Byte1 & 0x1F

   if self.CpuId == 0xFFE0:
     self.CpuTag = 0
   print "CpuTag:", self.CpuTag
   return self.CpuTag;
  
  def MemoryCheck(self,pic_data,MemoryBase,MemorySize):
    self.LoadMemoryAddress(MemoryBase)
    for l in range (MemorySize):
      Value = self.ReadMemoryNext()
      TargetValue = self.SearchByteValue(pic_data,l + MemoryBase)
      if(Value != TargetValue):
        print "  **** Address ", hex(l), " write  ", hex(TargetValue), " read" , hex(Value)
        return False
      if (l % 1024)==0 :
        sys.stdout.write('.')
        sys.stdout.flush()
    return True


  def IDCheck(self,pic_data):
     print "ID Check ",
     if self.MemoryCheck(pic_data,self.IDBase,self.IDSize):
       print " ... Passed!"
       return True
     return False


   
  def ProgramBlankCheck(self, numToCheck=None):
    print "Program code [", self.ProgramSize,"] blank check",
    self.LoadMemoryAddress(0)
    for l in range(self.ProgramSize if numToCheck is None else numToCheck):
      Value = self.ReadMemoryNext()
      if(Value != 0xff):
        print "*** CPU program at Address ", hex(l), " = ", hex(Value), " Failed!"
        return False
      if (l % 1024)==0 :
        sys.stdout.write('.')
        sys.stdout.flush()
    print "Passed!"
    return True


  def DataBlankCheck(self, checkSize=None):
    actualCheckSize = self.DataSize if checkSize is None else checkSize;
    print "EEPROM Blank Check "
    return self.DataCheck( None, actualCheckSize, 0xff)

  def DataCheck(self,pic_data, checkSize=None, checkValue=None ):
    actualCheckSize = self.DataSize if checkSize is None else checkSize;
    print "EEPROM DATA[",actualCheckSize,"]  Check ",
    #Direct access to data EEPROM
    self.LoadCode(0x9EA6)
    self.LoadCode(0x9CA6)
    for l in range( actualCheckSize):
      if (l % 32)==0 :
        sys.stdout.write('.')
        sys.stdout.flush()
      Value = checkValue if checkValue is not None else self.SearchByteValue(pic_data, l + self.DataBase)
      #Set data EEPROM Address Pointer
      self.LoadEepromAddress(l)
      #Initiate A memory Read
      self.LoadCode(0x80A6)
      #Load data into the serial data
      self.LoadCode(0x50A8)
      self.LoadCode(0x6EF5)
      self.LoadCode(0)
      self.LoadCommand(self.C_PIC18_TABLAT)
      RValue= self.ReadData()
      if Value != RValue :
        print "  *** EEROM  address ", hex(l), " write  ", hex(Value), " read" , hex(RValue)
        return False
    print "Done!"
    return True


  


  def ProgramCheck(self,pic_data, numToCheck=None):
    print "Program check ",
    if self.MemoryCheck(pic_data,self.ProgramBase, self.ProgramSize if numToCheck is None else numToCheck):
      print "Passed!"
      return True
    return False

  def MemoryDump(self,dump_base,dump_size):
    print ""
    print "----- MEMORY DUMP -----  BASE=", hex(dump_base)
    self.LoadCode(0)
    self.LoadMemoryAddress(dump_base)
    for l in range (dump_size):
      self.LoadMemoryAddress(dump_base+l)
      Value = self.ReadMemoryNext()
      if (l % 32) == 0:
       print format(l,'04x'), ":" ,
      else:
        if (l % 4) == 0:
          print "-",
      print format(Value,'02X'),
      if (l % 32) == 31:
       print " "
