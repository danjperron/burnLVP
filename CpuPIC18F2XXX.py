#!/usr/bin/env python

################################
#
#  Class to program PIC18F2XXX and PIC18F4XXX familly
#
#
#  class PIC18F2XXX 
#  inherit from class PIC18F
#
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



import burnGPIO
from time import sleep
import sys, termios, atexit
from intelhex import IntelHex
from select import select   
from  CpuPIC18F import PIC18F

class PIC18F2XXX(PIC18F):

  BufferSize =8
  
  #cpu List dict.  CpuId  [Name , IdMask, Revision Mask, Block Size, Block Count, Program Size]	

  ListName = 0
  ListMask = 1
  ListRMask = 2
  ListBlockSize = 3
  ListBlockCount = 4
  ListProgramSize = 5

  CpuList = {
               # ID         Name         IDMask  RevMask B.Size  B.Nb  P.Size 
		0x2160 : ['PIC18F2221' , 0xFFE0 , 0x1F , 0x0800 , 2 , 0x1000 ],
		0x2120 : ['PIC18F2321' , 0xFFE0 , 0x1F , 0x1000 , 2 , 0x2000 ],
		0x1160 : ['PIC18F2410' , 0xFFE0 , 0x1F , 0x2000 , 2 , 0x4000 ],
		0x1140 : ['PIC18F2420' , 0xFFF0 , 0x1F , 0x2000 , 2 , 0x4000 ],
		0x1150 : ['PIC18F2423' , 0xFFF0 , 0x1F , 0x2000 , 2 , 0x4000 ],
		0x2420 : ['PIC18F2450' , 0xFFE0 , 0x1F , 0x2000 , 2 , 0x4000 ],
		0x1260 : ['PIC18F2455' , 0xFFE0 , 0x1F , 0x2000 , 3 , 0x6000 ],
		0x2A60 : ['PIC18F2458' , 0xFFE0 , 0x1F , 0x2000 , 3 , 0x6000 ],
		0x1AE0 : ['PIC18F2480' , 0xFFE0 , 0x1F , 0x2000 , 2 , 0x4000 ],
		0x1120 : ['PIC18F2510' , 0xFFE0 , 0x1F , 0x2000 , 4 , 0x8000 ],
		0x0CE0 : ['PIC18F2515' , 0xFFE0 , 0x1F , 0x4000 , 3 , 0xC000 ],
		0x1100 : ['PIC18F2520' , 0xFFF0 , 0x1F , 0x2000 , 4 , 0x8000 ],
		0x1110 : ['PIC18F2523' , 0xFFF0 , 0x1F , 0x2000 , 4 , 0x8000 ],
		0x0CC0 : ['PIC18F2525' , 0xFFE0 , 0x1F , 0x4000 , 3 , 0xC000 ],
		0x1240 : ['PIC18F2550' , 0xFFE0 , 0x1F , 0x2000 , 4 , 0x8000 ],
		0x2A40 : ['PIC18F2553' , 0xFFE0 , 0x1F , 0x2000 , 4 , 0x8000 ],
		0x1AC0 : ['PIC18F2580' , 0xFFE0 , 0x1F , 0x2000 , 4 , 0x8000 ],
		0x0EE0 : ['PIC18F2585' , 0xFFE0 , 0x1F , 0x4000 , 3 , 0xC000 ],
		0x0CA0 : ['PIC18F2610' , 0xFFE0 , 0x1F , 0x4000 , 4 , 0x10000 ],
		0x0C80 : ['PIC18F2620' , 0xFFE0 , 0x1F , 0x4000 , 4 , 0x10000 ],
		0x0EE0 : ['PIC18F2680' , 0xFFE0 , 0x1F , 0x4000 , 4 , 0x10000 ],
		0x2700 : ['PIC18F2682' , 0xFFE0 , 0x1F , 0x4000 , 5 , 0x14000 ],
		0x2720 : ['PIC18F2685' , 0xFFE0 , 0x1F , 0x4000 , 6 , 0x18000 ],
		0x2140 : ['PIC18F4221' , 0xFFE0 , 0x1F , 0x0800 , 2 , 0x1000 ],
		0x2100 : ['PIC18F4321' , 0xFFE0 , 0x1F , 0x1000 , 2 , 0x2000 ],
		0x10E0 : ['PIC18F4410' , 0xFFE0 , 0x1F , 0x2000 , 2 , 0x4000 ],
		0x10C0 : ['PIC18F4420' , 0xFFF0 , 0x1F , 0x2000 , 2 , 0x4000 ],
		0x10D0 : ['PIC18F4423' , 0xFFF0 , 0x1F , 0x2000 , 2 , 0x4000 ],
		0x2400 : ['PIC18F4450' , 0xFFE0 , 0x1F , 0x2000 , 2 , 0x4000 ],
		0x1220 : ['PIC18F4455' , 0xFFE0 , 0x1F , 0x2000 , 3 , 0x6000 ],
		0x2A20 : ['PIC18F4458' , 0xFFE0 , 0x1F , 0x2000 , 3 , 0x6000 ],
		0x1AA0 : ['PIC18F4480' , 0xFFE0 , 0x1F , 0x2000 , 2 , 0x4000 ],
		0x10A0 : ['PIC18F4510' , 0xFFE0 , 0x1F , 0x2000 , 4 , 0x8000 ],
		0x0C60 : ['PIC18F4515' , 0xFFE0 , 0x1F , 0x4000 , 3 , 0xC000 ],
		0x1080 : ['PIC18F4520' , 0xFFF0 , 0x1F , 0x2000 , 4 , 0x8000 ],
		0x1090 : ['PIC18F4523' , 0xFFF0 , 0x1F , 0x2000 , 4 , 0x8000 ],
		0x0C40 : ['PIC18F4525' , 0xFFE0 , 0x1F , 0x4000 , 3 , 0xC000 ],
		0x1200 : ['PIC18F4550' , 0xFFE0 , 0x1F , 0x2000 , 4 , 0x8000 ],
		0x2A00 : ['PIC18F4553' , 0xFFE0 , 0x1F , 0x2000 , 4 , 0x8000 ],
		0x1A80 : ['PIC18F4580' , 0xFFE0 , 0x1F , 0x2000 , 4 , 0x8000 ],
		0x0EA0 : ['PIC18F4585' , 0xFFE0 , 0x1F , 0x4000 , 3 , 0xC000 ],
		0x0C20 : ['PIC18F4610' , 0xFFE0 , 0x1F , 0x4000 , 4 , 0x10000 ],
		0x0C00 : ['PIC18F4620' , 0xFFE0 , 0x1F , 0x4000 , 4 , 0x10000 ],
		0x0E80 : ['PIC18F4680' , 0xFFE0 , 0x1F , 0x4000 , 4 , 0x10000 ],
		0x2740 : ['PIC18F4682' , 0xFFE0 , 0x1F , 0x4000 , 5 , 0x14000 ],
		0x2760 : ['PIC18F4685' , 0xFFE0 , 0x1F , 0x4000 , 6 , 0x18000 ]
             }

  PicFamilly = 'PIC18F2XXX'
 

  def BulkErase(self):
    print "Bulk Erase ",
    self.LoadCode(0x8EA6)
    self.LoadCode(0x8CA6)
    self.LoadCode(0x86A6)
    self.LoadMemoryAddress(0x3C0004)
    self.LoadCommandWord(self.C_PIC18_WRITE,0x0080)
    self.LoadCode(0)
    self.LoadCommand(self.C_PIC18_NOP)
    sleep(0.015)
    self.LoadWord(0)
    print "..... Done!"


#Multi Panel code programming
  def ProgramBurn(self, pic_data):
    print "Writing Program",
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
    print "Done!"




       


  def  DataBurn(self,pic_data):
    print "Writing EEPROM data[",self.DataSize,"]",
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
    print "Done!"


  def DataEepromCheckPic18(self,pic_data):
    print "EEROM Data Check",
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
        print "  *** EEROM  address ", hex(l), " write  ", hex(Value), " read" , hex(RValue)
        return False
    print "Done!"
    return True
   


  def IDBurn(self,pic_data):
    print "Writing ID",
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
    print " ... Done!"
    return  

#  def IDCheck(self,pic_data):
#     print "ID Check ",
#     if MemoryCheck(pic_data,self.IDBase,self.IDSize):
#       print " ... Passed!"
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
    print "CONFIG Burn",
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
      self.LoadCommandWord(self.C_PIC18_WRITE,self.ConfigMirror[l])
      self.WriteAndWait()
      self.LoadCode(0x2AF6)
      self.LoadCommandWord(self.C_PIC18_WRITE,self.ConfigMirror[l])
      self.WriteAndWait()
    print " ... Done!"
    
   

  def ConfigCheck(self,pic_data):
    print "Config Check ",
    self.AnalyzeConfig(pic_data)
    self.LoadMemoryAddress(self.ConfigBase)
    for l in range (14):
      Value = self.ReadMemoryNext()
      if (l & 1) == 0 :
         TargetValue = self.ConfigMirror[l / 2] & 0xff
      else:
         TargetValue = (self.ConfigMirror[l/2] >> 8) & 0xff
      if(Value != TargetValue):
        print "  **** Address ", hex(l), " write  ", hex(TargetValue), " read" , hex(Value)
        return False
      if (l % 1024)==0 :
        sys.stdout.write('.')
        sys.stdout.flush()
    print " ... Passed!"
    return True



  ListName = 0
  ListMask = 1
  ListRMask = 2
  ListBlockSize = 3
  ListBlockCount = 4
  ListProgramSize = 5

  def FindCpu(self, Id):
    #scan the list and find cpu corresponding with the CpuTag
    #some cpu use bit 4 from revision for cpu identification
    for l in self.CpuList:
       _cpuInfo =self.CpuList.get(l)
       #get IdMask from specific cpu 
       _cpuID = _cpuInfo[self.ListMask] & Id
       if _cpuID == l:
         self.ProgramSize = _cpuInfo[self.ListProgramSize]
         self.BlockCount  = _cpuInfo[self.ListBlockCount]
         self.CpuId = _cpuID
         self.CpuRevision = Id & _cpuInfo[self.ListRMask]
         return _cpuInfo 
    return  None



