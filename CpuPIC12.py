#!/usr/bin/env python3

################################
#
# CpuPIC1.py  
#
#
# burnLVP Pic12 Class module
#
#
# programmer : Daniel Perron
# Date       : Sept. 20J, 2013
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


class PIC12:

  CpuTag=0
  CpuId=0
  CpuRevision=0

  ProgramSize = 2048
  ProgramBase = 0

  DataSize    = 256    
  DataBase    = 0x1e000

  ConfigBase  = 0x10000
  
  PicFamily = "PIC12/16"




  #cpu list  dict.   CpuId [Pic Name, ProgramSize]
  CpuList =  {  0x1b80 : ['PIC12F1840'  , 4096] ,
                0x1bc0 : ['PIC12LF1840' , 4096] , 
                0x1480 : ['PIC16F1847'  , 8192] ,
                0x14A0 : ['PIC16LF1847' , 8192] ,
                0x2780 : ['PIC16F1826'  , 2048] ,
                0x2880 : ['PIC16LF1826' , 2048] ,
                0x27A0 : ['PIC16F1827'  , 4096] ,
                0x28A0 : ['PIC16LF1827' , 4096] ,
		0x2720 : ['PIC16F1823'  , 2048] ,
                0x2820 : ['PIC16LF1823' , 2048] ,
                0x2700 : ['PIC12F1822'  , 2048] ,
		0x2800 : ['PIC12LF1822' , 2048] ,
                0x2740 : ['PIC16F1824'  , 4096] ,
                0x2840 : ['PIC16LF1824' , 4096] ,
                0x2760 : ['PIC16F1825'  , 4096] ,
                0x2860 : ['PIC16LF1825' , 4096] ,
                0x27C0 : ['PIC16F1828'  , 4096] ,
                0x28C0 : ['PIC16LF1828' , 4096] ,
                0x27E0 : ['PIC16F1829'  , 8192] ,
                0x28E0 : ['PIC16LF1829' , 8192]
             }

  # command definition
  C_LOAD_CONFIG = 0
  C_LOAD_PROGRAM = 2 
  C_LOAD_DATA   =  3
  C_READ_PROGRAM = 4
  C_READ_DATA    = 5
  C_INC_ADDRESS = 6
  C_RESET_ADDRESS = 0x16
  C_BEGIN_INT_PROG = 8
  C_BEGIN_EXT_PROG = 0x18
  C_END_EXT_PROG = 0xa
  C_BULK_ERASE_PROGRAM = 9
  C_BULK_ERASE_DATA = 0xB


  def Set_LVP(self):
    #held MCLR HIGH
    IO.GPIO.output(IO.PIC_MCLR, True)
    sleep(0.1)
    #ok PIC_CLK=out& HIGH, PIC_DATA=out & LOW
    IO.GPIO.output(IO.PIC_CLK, False)
    #MCLR LOW 
    IO.GPIO.output(IO.PIC_DATA, False)
#    print("LVP ON")
    IO.GPIO.output(IO.PIC_MCLR, False)
    sleep(0.3)

  def Release_LVP(self):

    IO.GPIO.output(IO.PIC_MCLR, True)
    sleep(0.1)
    IO.GPIO.output(IO.PIC_MCLR, False)
#    print("LVP OFF")

  def SendMagic(self):
    magic = 0x4d434850
    IO.GPIO.setup(IO.PIC_DATA, IO.GPIO.OUT)   
    for loop in range(33):
      IO.GPIO.output(IO.PIC_CLK, True)
      IO.GPIO.output(IO.PIC_DATA, (magic & 1) == 1)
      pass
      IO.GPIO.output(IO.PIC_CLK, False)
      pass
      magic = magic >> 1


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
    print("Bulk Erase Program",end='')
    self.SendCommand(self.C_RESET_ADDRESS)
    self.SendCommand(self.C_LOAD_CONFIG)
    self.LoadWord(0x3fff)
    self.SendCommand(self.C_BULK_ERASE_PROGRAM)
    sleep(0.1)
    print(", Data.",end='')
    self.SendCommand(self.C_BULK_ERASE_DATA)
    sleep(0.1)
    print(".... done.")


  def ProgramBlankCheck(self):
    print("Program blank check",end='')
    self.SendCommand(self.C_RESET_ADDRESS)
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
    self.SendCommand(self.C_RESET_ADDRESS)
    for l in range(self.DataSize):
      self.SendCommand(self.C_READ_DATA)
      Value = self.ReadWord()
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
    self.SendCommand(self.C_RESET_ADDRESS)
    for l in range(self.ProgramSize):
      if pic_data.get(l*2+ self.ProgramBase) != None :
        if pic_data.get(l*2+ self.ProgramBase+1) != None :
          Value = pic_data.get(l*2+ self.ProgramBase) + ( 256 * pic_data.get(l*2+ self.ProgramBase+1))
          Value = Value & 0x3fff
          self.SendCommand(self.C_LOAD_PROGRAM)
          self.LoadWord(Value)
          self.SendCommand(self.C_BEGIN_INT_PROG)
          sleep(0.005)
          self.SendCommand(self.C_READ_PROGRAM)
          RValue = self.ReadWord()
          if Value != RValue :
            print("Program address:", hex(l) , " write ", hex(Value), " read ", hex(RValue), " Failed!")
            return False
      if (l % 128)==0 :
        sys.stdout.write('.')
        sys.stdout.flush()
      self.SendCommand(self.C_INC_ADDRESS)
    print("Done.")
    return True

  def DataBurn(self,pic_data):
    print("Writing Data",end='')
    self.SendCommand(self.C_RESET_ADDRESS)
    for l in range( self.DataSize):
     if pic_data.get(l*2 + self.DataBase) != None :
      if pic_data.get(l*2 + self.DataBase + 1) != None :
        Value = pic_data.get(l*2 + self.DataBase)
        self.SendCommand(self.C_LOAD_DATA)
        self.LoadWord(Value)
        self.SendCommand(self.C_BEGIN_INT_PROG)
        sleep(0.003)
        self.SendCommand(self.C_READ_DATA)
        RValue = self.ReadWord()
        if Value != RValue :
          print("Data address:", hex(l) , " write ", hex(Value), " read ", hex(RValue), " Failed!")
          return False
      if (l % 32)==0 :
        sys.stdout.write('.')
        sys.stdout.flush()
      self.SendCommand(self.C_INC_ADDRESS)
    print("Done.")
    return True

  def ProgramCheck(self, pic_data):
    print("Program check ",end='')
    self.SendCommand(self.C_RESET_ADDRESS)
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
    self.SendCommand(self.C_RESET_ADDRESS)
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
    self.SendCommand(self.C_RESET_ADDRESS)
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
          self.SendCommand(self.C_BEGIN_INT_PROG)
          sleep(0.005)
          self.SendCommand(self.C_READ_PROGRAM)
          RValue = self.ReadWord()
          if Value != RValue :
            print("User Id Location:", hex(l) , " write ", hex(Value), " read ", hex(RValue), " Failed!")
            return False
        sys.stdout.write('.')
        sys.stdout.flush()
      self.SendCommand(self.C_INC_ADDRESS)
    #ok we are at 08004
    #skip 0x8004 .. 0x8006
    self.SendCommand(self.C_INC_ADDRESS)
    self.SendCommand(self.C_INC_ADDRESS)
    self.SendCommand(self.C_INC_ADDRESS)
    # now the configuration word 1& 2  at 0x8007 ( hex file at 0x1000E)
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
          self.SendCommand(self.C_BEGIN_INT_PROG)
          sleep(0.005)
          self.SendCommand(self.C_READ_PROGRAM)
          RValue = self.ReadWord()
          if Value != RValue :
            print("Config Word ", l-6 , " write ", hex(Value), " read ", hex(RValue), " Failed!")
            return False
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
    self.SendCommand(self.C_RESET_ADDRESS)
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
    #ok we are at 08004
    #skip 0x8004 .. 0x8006
    self.SendCommand(self.C_INC_ADDRESS)
    self.SendCommand(self.C_INC_ADDRESS)
    self.SendCommand(self.C_INC_ADDRESS)
    # now the configuration word 1& 2  at 0x8007 ( hex file at 0x1000E)
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
    print("Check PIC12/16...")
    self.Set_LVP()
    self.SendMagic()
    self.SendCommand(0)
    self.LoadWord(0x3FFF)
    for l in range(6):
      self.SendCommand(self.C_INC_ADDRESS)
    self.SendCommand(self.C_READ_PROGRAM)
    self.CpuTag=self.ReadWord()
    self.CpuRevision = self.CpuTag & 0x1f
    self.CpuId = self.CpuId & 0x3FE0
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



