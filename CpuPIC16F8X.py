#!/usr/bin/env python3

################################
#
# CpuPIC16F8x.py
#
#
# burnLVP Pic16F87/88 Class module
#
#
# programmer : Daniel Perron
# Date       : Dec 5, 2017
# Version    : 1.0
#
# modified version of original burnLVP
# source code:  https://github.com/danjperron/A2D_PIC_RPI
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
#	CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE

#import GPIO interface
import burnGPIO      as IO


from time import sleep
import sys, termios, atexit
from intelhex import IntelHex
from select import select


class PIC16F8X:

  CpuTag=0
  CpuId=0
  CpuRevision=0

  ProgramSize = 2048
  ProgramBase = 0

  DataSize    = 256
  DataBase    = 0x2100

  ConfigBase  = 0x2000

  PicFamily = "PIC12/16"




  #cpu list  dict.   CpuId [Pic Name, ProgramSize]
  CpuList =  {  0x0720 : ['PIC16F87'  , 4096] ,
                0x0760: ['PIC16F88' , 4096] ,
             }

  # command definition
  C_LOAD_CONFIG = 0
  C_LOAD_PROGRAM = 2
  C_LOAD_DATA   =  3
  C_READ_PROGRAM = 4
  C_READ_DATA    = 5
  C_INC_ADDRESS = 6
  C_BEGIN_ERASE = 8
  C_BEGIN_PROGRAMMING  =0x18
  C_BULK_ERASE_PROGRAM = 9
  C_BULK_ERASE_DATA = 0xB
  C_END_PROGRAMMING = 0x17
  C_CHIP_ERASE = 0x1F


  def Set_LVP(self):
    IO.GPIO.setup(IO.PIC_DATA,IO.GPIO.OUT)
    IO.GPIO.output(IO.PIC_DATA, False)
    IO.GPIO.output(IO.PIC_CLK, False)
    #PGM LOW
    IO.GPIO.output(IO.PIC_PGM,False)
    #MCLR LOW
    IO.GPIO.output(IO.PIC_MCLR, False)
    #PGM HIGH
    IO.GPIO.output(IO.PIC_PGM,True)
    #held MCLR HIGH
    IO.GPIO.output(IO.PIC_MCLR, True)
    sleep(0.1)
    #ok PIC_CLK=out& HIGH, PIC_DATA=out & LOW
    IO.GPIO.output(IO.PIC_CLK, False)
#    print("LVP ON")
    sleep(0.3)

  def Release_LVP(self):

    IO.GPIO.output(IO.PIC_MCLR, False)
    sleep(0.1)
    IO.GPIO.output(IO.PIC_PGM, False)
    IO.GPIO.output(IO.PIC_MCLR, True)

#    print("LVP OFF")


  def SendCommand(self,Command):
    IO.GPIO.setup( IO.PIC_DATA, IO.GPIO.OUT)
    for loop in range(6):
      IO.GPIO.output(IO.PIC_CLK, True)
      IO.GPIO.output(IO.PIC_DATA, (Command & 1) ==1)
      pass
      IO.GPIO.output(IO.PIC_CLK, False)
      pass
      Command = Command >> 1;


  def ReadWord(self):
    IO.GPIO.setup(IO.PIC_DATA, IO.GPIO.IN)
    Value = 0
    for loop in range(16):
      IO.GPIO.output(IO.PIC_CLK, True)
      pass
      if IO.GPIO.input(IO.PIC_DATA):
        Value =  Value + (1 << loop)
      IO.GPIO.output(IO.PIC_CLK, False)
      pass
    Value = (Value >> 1) & 0x3FFF;
    return Value;


  def LoadWord(self,Value):
    IO.GPIO.setup(IO.PIC_DATA, IO.GPIO.OUT)
    Value = (Value << 1) & 0x7FFE
    for loop in range(16):
      IO.GPIO.output(IO.PIC_CLK, True)
      IO.GPIO.output(IO.PIC_DATA,(Value & 1)==1)
      pass
      IO.GPIO.output(IO.PIC_CLK, False)
      pass
      Value = Value >> 1;

  def BulkErase(self):
    self.Set_LVP();
    self.SendCommand(self.C_LOAD_CONFIG)
    self.LoadWord(0x3fff)
    print("Chip Erase Chip",end='')
    self.SendCommand(self.C_CHIP_ERASE)
    sleep(0.2)
    print(".... done.")


  def ProgramBlankCheck(self):
    print("Program blank check",end='')
    #reset address
    self.Set_LVP()
    for l in range(self.ProgramSize):
      self.SendCommand(self.C_READ_PROGRAM)
      Value = self.ReadWord()
      if  Value != 0x3fff :
        print("*** CPU program at Address ", hex(l), " = ", hex(Value), " Failed!")
        return False
      if (l % 128)==0 :
       sys.stdout.write('.')
       sys.stdout.flush()
      self.SendCommand(self.C_INC_ADDRESS)
    print("Passed!")
    return True

  def DataBlankCheck(self):
    print("Data Blank check",end='')
    self.Set_LVP()
    for l in range(self.DataSize):
      self.SendCommand(self.C_READ_DATA)
      Value = self.ReadWord() & 0xff
      if  Value != 0xff :
        print("*** CPU eeprom data  at Address ", hex(l), " = ", hex(Value), "Failed!")
        return False
      if (l % 32)==0 :
        sys.stdout.write('.')
        sys.stdout.flush()
      self.SendCommand(self.C_INC_ADDRESS)
    print("Passed!")
    return True


  def ProgramBurn(self, pic_data):
    print("Writing Program",end='')
    self.Set_LVP()
    for i in range(0,self.ProgramSize,4):
      for DataCount in range(4):
        l =  i + DataCount
        if pic_data.get(l*2+ self.ProgramBase) != None :
          if pic_data.get(l*2+ self.ProgramBase+1) != None :
           Value = pic_data.get(l*2+ self.ProgramBase) + ( 256 * pic_data.get(l*2+ self.ProgramBase+1))
           Value = Value & 0x3fff
           self.SendCommand(self.C_LOAD_PROGRAM)
           self.LoadWord(Value)
        if DataCount != 3:
           self.SendCommand(self.C_INC_ADDRESS)
      if (i % 128)==0 :
        sys.stdout.write('.')
        sys.stdout.flush()
      #ok 4 words then write 
      self.SendCommand(self.C_BEGIN_PROGRAMMING)
      sleep(0.005)
      self.SendCommand(self.C_END_PROGRAMMING)
      self.SendCommand(self.C_INC_ADDRESS)
    print("Done.")
    return True

  def DataBurn(self,pic_data):
    print("Writing Data",end='')
    self.Set_LVP()
    for l in range( self.DataSize):
     if pic_data.get(l*2 + self.DataBase) != None :
      if pic_data.get(l*2 + self.DataBase + 1) != None :
        Value = pic_data.get(l*2 + self.DataBase)
        self.SendCommand(self.C_LOAD_DATA)
        self.LoadWord(Value)
        self.SendCommand(self.C_BEGIN_PROGRAMMING)
        sleep(0.003)
        self.SendCommand(self.C_END_PROGRAMMING)
      if (l % 32)==0 :
        sys.stdout.write('.')
        sys.stdout.flush()
      self.SendCommand(self.C_INC_ADDRESS)
    print("Done.")
    return True

  def ProgramCheck(self, pic_data):
    print("Program check ",end='')
    self.Set_LVP()
    for l in range(self.ProgramSize):
      if pic_data.get(l*2+ self.ProgramBase) != None :
        if pic_data.get(l*2+ self.ProgramBase+1) != None :
          Value = pic_data.get(l*2+ self.ProgramBase) + ( 256 * pic_data.get(l*2+ self.ProgramBase+1))
          Value = Value & 0x3fff
          self.SendCommand(self.C_READ_PROGRAM)
          RValue = self.ReadWord()
          if Value != RValue :
            print("Program address:", hex(l) , " write ", hex(Value), " read ", hex(RValue))
            return False
      if (l % 128)==0 :
        sys.stdout.write('.')
        sys.stdout.flush()
      self.SendCommand(self.C_INC_ADDRESS)
    print("Passed!")
    return True



  def DataCheck(self,pic_data):
    print("Data check ",end='')
    self.Set_LVP()
    for l in range(self.DataSize):
     if pic_data.get(l*2 + self.DataBase) != None :
      if pic_data.get(l*2 + self.DataBase+1) != None :
        Value = pic_data.get(l*2+self.DataBase)
        self.SendCommand(self.C_READ_DATA)
        RValue = self.ReadWord()
        if Value != RValue :
           print("Data address:", hex(l) , " write ", hex(Value), " read ", hex(RValue))
           return False
      if (l % 32)==0 :
        sys.stdout.write('.')
        sys.stdout.flush()
      self.SendCommand(self.C_INC_ADDRESS)
    print("Passed!")
    return True


  def ConfigBurn(self,pic_data):
    print("Writing Config",end='')
    self.Set_LVP()
    self.SendCommand(self.C_LOAD_CONFIG)
    self.LoadWord(0x3fff)
    #user id first
    for l in range(4):
      if pic_data.get(l*2+ self.ConfigBase) != None :
        if pic_data.get(l*2+ self.ConfigBase+1) != None :
          Value = pic_data.get(l*2+ self.ConfigBase) + ( 256 * pic_data.get(l*2+ self.ConfigBase+1))
          Value = Value & 0x3fff
          self.SendCommand(self.C_LOAD_PROGRAM)
          self.LoadWord(Value)
          if l != 3 :
            self.SendCommand(self.C_INC_ADDRESS)
    self.SendCommand(self.C_BEGIN_PROGRAMMING)
    sleep(0.005)
    self.SendCommand(self.C_END_PROGRAMMING)
    self.SendCommand(self.C_INC_ADDRESS)
    sys.stdout.write('.')
    sys.stdout.flush()
    #ok we are at 02004
    #skip 0x2004 .. 0x2006
    self.SendCommand(self.C_INC_ADDRESS)
    self.SendCommand(self.C_INC_ADDRESS)
    self.SendCommand(self.C_INC_ADDRESS)
    # now the configuration word 1& 2  at 0x2007 ( hex file at 0x1000E)
    for l in range(7,9):
      if pic_data.get(l*2+ self.ConfigBase) != None :
        if pic_data.get(l*2+ self.ConfigBase+1) != None :
          Value = pic_data.get(l*2+ self.ConfigBase) + ( 256 * pic_data.get(l*2+ self.ConfigBase+1))
          Value = Value & 0x3fff
          self.SendCommand(self.C_LOAD_PROGRAM)
          if l is 8:
            #catch21 force LVP programming to be always ON
            Value = Value | 0x2000
          self.LoadWord(Value)
          self.SendCommand(self.C_BEGIN_PROGRAMMING)
          sleep(0.005)
          self.SendCommand(self.C_END_PROGRAMMING)
      sys.stdout.write('.')
      sys.stdout.flush()
      self.SendCommand(self.C_INC_ADDRESS)
    print("Done.")
    return True


#just check if the user forget to set LVP flag enable
#if not just give a warning since we force LVP enable

  def CheckLVP(self,pic_data):
     #specify config word2
    l=8
    if pic_data.get(l*2+ self.ConfigBase) != None :
      if pic_data.get(l*2+ self.ConfigBase+1) != None :
        Value = pic_data.get(l*2+ self.ConfigBase) + ( 256 * pic_data.get(l*2+ self.ConfigBase+1))
        Value = Value & 0x3fff
        return((Value & 0x2000)== 0x2000)
    return True



  def ConfigCheck(self, pic_data):
    print("Config Check",end='')
    self.Set_LVP()
    self.SendCommand(self.C_LOAD_CONFIG)
    self.LoadWord(0x3fff)
    #user id first
    for l in range(4):
      if pic_data.get(l*2+ self.ConfigBase) != None :
        if pic_data.get(l*2+ self.ConfigBase+1) != None :
          Value = pic_data.get(l*2+ self.ConfigBase) + ( 256 * pic_data.get(l*2+ self.ConfigBase+1))
          Value = Value & 0x3fff
          self.SendCommand(self.C_READ_PROGRAM)
          RValue = self.ReadWord()
          if Value != RValue :
            print("User Id Location:", hex(l) , " write ", hex(Value), " read ", hex(RValue), " Failed!")
            return False
        sys.stdout.write('.')
        sys.stdout.flush()
      self.SendCommand(self.C_INC_ADDRESS)
    #ok we are at 0x2004
    #skip 0x2004 .. 0x2006
    self.SendCommand(self.C_INC_ADDRESS)
    self.SendCommand(self.C_INC_ADDRESS)
    self.SendCommand(self.C_INC_ADDRESS)
    # now the configuration word 1& 2  at 0x2007
    for l in range(7,9):
      if pic_data.get(l*2+ self.ConfigBase) != None :
        if pic_data.get(l*2+ self.ConfigBase+1) != None :
          Value = pic_data.get(l*2+ self.ConfigBase) + ( 256 * pic_data.get(l*2+ self.ConfigBase+1))
          Value = Value & 0x3fff
          if l is 8:
            #catch21 force LVP programming to be always ON
            Value = Value | 0x2000
          self.SendCommand(self.C_READ_PROGRAM)
          RValue = self.ReadWord()
          if Value != RValue :
            print("Config Word ", l-6 , " write ", hex(Value), " read ", hex(RValue), " Failed!")
            return False
        sys.stdout.write('.')
        sys.stdout.flush()
      self.SendCommand(self.C_INC_ADDRESS)
    print("Passed!")
    self.CheckLVP(pic_data)
    return True

  def IDBurn(self, pic_data):
    #ID is with CONFIG
    pass

  def IDCheck(self, pic_data):
    #id is with CONFIG
    return True


  def ScanCpuTag(self):
    print("Check PIC16F87/88...")
    self.Set_LVP()
    self.SendCommand(0)
    self.LoadWord(0x3FFF)
    for l in range(6):
      self.SendCommand(self.C_INC_ADDRESS)
    self.SendCommand(self.C_READ_PROGRAM)
    self.CpuTag=self.ReadWord()
    self.CpuRevision = self.CpuTag & 0x1f
    self.CpuId = self.CpuTag & 0x3FE0
    if ((self.CpuTag & 0x3FE0)  == 0x3FE0):
      self.CpuTag=0
    return self.CpuTag


  ListName=0
  ListProgramSize=1

  def FindCpu(self, Id):
    _cpuInfo = self.CpuList.get(Id & 0xFFE0)
    if _cpuInfo != None:
      self.ProgramSize= _cpuInfo[self.ListProgramSize]
      self.CpuId = Id & 0XFFE0
      self.CpuRevision= Id & 0x1F
    return _cpuInfo



