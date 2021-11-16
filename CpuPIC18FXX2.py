#!/usr/bin/env python3

################################
#
#  Class to program PIC18FXX8 and PIC18FXX2 family
#
#
#  class PIC18FXX8 
#  inherit from class PIC18F
#
#
# programmer : Daniel Perron
# Date       : Sept 26, 2013
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



import burnGPIO
from time import sleep
import sys, termios, atexit
from intelhex import IntelHex
from select import select   
from  CpuPIC18F import PIC18F

class PIC18FXX2(PIC18F):
  


  PanelSize = 0x2000
  BufferSize =8
  
  #cpu list  dict.   CpuId [Name, program Size]
  CpuList = { 0x0480 : ['PIC18F242' , 16384],
              0x0800 : ['PIF18F248' , 16384],
              0x0400 : ['PIC18F252' , 32768],
              0x0840 : ['PIC18F258' , 32768],
              0x04A0 : ['PIC18F442' , 16384],
              0x0820 : ['PIC18F448' , 16384],
              0x0420 : ['PIC18F452' , 32768],
              0x0860 : ['PIC18F458' , 32768]
             }

  PicFamily = 'PIC18FXX2'
 


  def BulkErase(self):
    print("Bulk Erase ",end='')
    self.LoadCode(0x8EA6)
    self.LoadCode(0x8CA6)
    self.LoadCode(0x86A6)
    self.LoadMemoryAddress(0x3C0004)
    self.LoadCommandWord(self.C_PIC18_WRITE,0x0080)
    self.LoadCode(0)
    self.LoadCommand(self.C_PIC18_NOP)
    sleep(0.015)
    self.LoadWord(0)
    print("..... Done!")


#Multi Panel code programming
  def ProgramBurn(self, pic_data):
    print("Writing Program",end='')
    NumberOfPanel = self.ProgramSize / self.PanelSize 
    self.LoadCode(0x8EA6)
    self.LoadCode(0x8CA6)
    self.LoadCode(0x86A6)
    WaitFlag= False
    for CountIdx in range(0,self.PanelSize,self.BufferSize):
      self.LoadMemoryAddress(0x3C0006)
      self.LoadCommandWord(self.C_PIC18_WRITE,0x0040)

      self.LoadCode(0x8EA6)
      self.LoadCode(0x9CA6)

      for PanelIdx in range(NumberOfPanel):
        AddressOffset = CountIdx + (PanelIdx * self.PanelSize)
        self.LoadMemoryAddress(AddressOffset)  
        for DataWordIdx in range(0,self.BufferSize,2):
          if DataWordIdx == 6 :
            if PanelIdx == (NumberOfPanel -1):
              WaitFlag= True
              self.LoadCommand(self.C_PIC18_START_PGM)
            else:
              self.LoadCommand(self.C_PIC18_WRITE)
          else:
            self.LoadCommand(self.C_PIC18_WRITE_INC_BY2)
          PAddress = AddressOffset + DataWordIdx  + self.ProgramBase;
          self.LoadWord(self.SearchWordValue(pic_data,PAddress))
          if WaitFlag:
            self.WriteAndWait()
            WaitFlag= False;
      if (CountIdx % 256)==0:
        sys.stdout.write('.')
        sys.stdout.flush()
    print("Done!")




       


  def  DataBurn(self,pic_data):
    print("Writing EEPROM data[",self.DataSize,"]",end="")
    #direct access to data EEPROM
    self.LoadCode(0x9EA6)
    self.LoadCode(0x9CA6)
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
      self.LoadCode(0x6EA8)
      #enable memory writes
      self.LoadCode(0x84A6) 
      #perfom required sequence
      self.LoadCode(0x0E55)
      self.LoadCode(0x6EA7)
      self.LoadCode(0x0EAA)
      self.LoadCode(0x6EA7)
      #initiate write
      self.LoadCode(0x82A6)
      while True:
        #Poll WR bit,
        self.LoadCode(0x50A6)
        self.LoadCode(0x6EF5)
        self.LoadCommandPic18(self.C_PIC18_TABLAT)
        EECON1 = self.ReadDataPic18()
        if (EECON1 & 2) == 0:
          break
      self.LoadCode(0x94A6)
    print("Done!")


  def DataEepromCheckPic18(self,pic_data):
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
   


  def IDBurn(self,pic_data):
    print("Writing ID",end='')
    #direct access config memory
    self.LoadCode(0x8EA6)
    self.LoadCode(0x8CA6)
    #configure single Panel
    self.LoadMemoryAddress(0x3C0006)
    self.LoadCommandWord(self.C_PIC18_WRITE,0)
    #Direct access to code memory
    self.LoadCode(0x8EA6)
    self.LoadCode(0x9CA6)
    #Load Write buffer
    self.LoadMemoryAddress(0x200000)
    self.LoadCommandWord(self.C_PIC18_WRITE_INC_BY2, self.SearchWordValue(pic_data,self.IDBase))
    self.LoadCommandWord(self.C_PIC18_WRITE_INC_BY2, self.SearchWordValue(pic_data,self.IDBase+2))
    self.LoadCommandWord(self.C_PIC18_WRITE_INC_BY2, self.SearchWordValue(pic_data,self.IDBase+4))
    self.LoadCommandWord(self.C_PIC18_START_PGM, self.SearchWordValue(pic_data,self.IDBase+6))
    self.WriteAndWait()   
    print(" ... Done!")
    return  

#  def IDCheck(self,pic_data):
#     print("ID Check ",
#     if MemoryCheck(pic_data,self.IDBase,self.IDSize):
#       print(" ... Passed!"
#       return True  
#     return False
   


  #create a config Mirror of 7 WORDS 
  ConfigMirror = [0xFFFF] * 7

  def AnalyzeConfig(self,pic_data):
    self.ConfigMirror
    ConfigMask= [0x2700,0x0f0f,0x0100,0x0085,0xc00f,0xe00f,0x400f]
    #transfer Config1 .. Config7  and use mask
    for l in range(7):
      self.ConfigMirror[l] = self.SearchWordValue(pic_data, self.ConfigBase + (l * 2)) & ConfigMask[l]   
    #fix LVP in CONFIG4L  Force LVP
    self.ConfigMirror[3] = self.ConfigMirror[3] | 0x0004
   

  def ConfigBurn(self,pic_data):
    print("CONFIG Burn",end='')
    self.AnalyzeConfig(pic_data)
    #burn all config but CONFIG6 last because of WRTC
    for l in range(5)+[6,5]:
      #direct access config memory
      self.LoadCode(0x8EA6)
      self.LoadCode(0x8CA6)
      #position program counter
      self.LoadCode(0xEF00)
      self.LoadCode(0xF800)
      #Set Table Pointer 
      self.LoadMemoryAddress(self.ConfigBase+(l*2))
      self.LoadCode(0x6EF6)
      self.LoadCommandWord(self.C_PIC18_START_PGM,self.ConfigMirror[l])
      self.WriteAndWait()
      self.LoadCode(0x2AF6)
      self.LoadCommandWord(self.C_PIC18_START_PGM,self.ConfigMirror[l])
      self.WriteAndWait()
    print(" ... Done!")
    
   

  def ConfigCheck(self,pic_data):
    print("Config Check ",end='')
    self.AnalyzeConfig(pic_data)
    self.LoadMemoryAddress(self.ConfigBase)
    for l in range (14):
      Value = self.ReadMemoryNext()
      if (l & 1) == 0 :
         TargetValue = self.ConfigMirror[l / 2] & 0xff
      else:
         TargetValue = (self.ConfigMirror[l/2] >> 8) & 0xff
      if(Value != TargetValue):
        print("  **** Address ", hex(l), " write  ", hex(TargetValue), " read" , hex(Value))
        return False
      if (l % 1024)==0 :
        sys.stdout.write('.')
        sys.stdout.flush()
    print(" ... Passed!")
    return True



  def FindCpu(self, Id):
    cpuinfo= self.CpuList.get(Id & 0xFFE0)
    if cpuinfo!= None:
       self.ProgramSize = cpuinfo[1]
    return  cpuinfo



