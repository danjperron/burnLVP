#!/usr/bin/env python

################################
#
#  Class to program PIC18F2XXX and PIC18F4XXX family
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

  WriteBufferSize =8
  EraseBufferSize =64
  #cpu List dict.  CpuId  [Name , IdMask, Revision Mask, Block Size, Block Count, Program Size, WriteBuffer]	

  ListName = 0
  ListMask = 1
  ListRMask = 2
  ListBlockSize = 3
  ListBlockCount = 4
  ListProgramSize = 5
  ListWriteBufferSize = 6

  CpuList = {
               # ID         Name        IDMask  RevMask B.Size  B.Nb  P.Size W.Buf
		0x2160 : ['PIC18F2221' , 0xFFE0 , 0x1F , 0x0800 , 2 , 0x1000 , 8   ],
		0x2120 : ['PIC18F2321' , 0xFFE0 , 0x1F , 0x1000 , 2 , 0x2000 , 8   ],
		0x1160 : ['PIC18F2410' , 0xFFE0 , 0x1F , 0x2000 , 2 , 0x4000 , 32  ],
		0x1140 : ['PIC18F2420' , 0xFFF0 , 0x1F , 0x2000 , 2 , 0x4000 , 32  ],
		0x1150 : ['PIC18F2423' , 0xFFF0 , 0x1F , 0x2000 , 2 , 0x4000 , 32  ],
		0x2420 : ['PIC18F2450' , 0xFFE0 , 0x1F , 0x2000 , 2 , 0x4000 , 16  ],
		0x1260 : ['PIC18F2455' , 0xFFE0 , 0x1F , 0x2000 , 3 , 0x6000 , 32  ],
		0x2A60 : ['PIC18F2458' , 0xFFE0 , 0x1F , 0x2000 , 3 , 0x6000 , 32  ],
		0x1AE0 : ['PIC18F2480' , 0xFFE0 , 0x1F , 0x2000 , 2 , 0x4000 , 32  ],
		0x1120 : ['PIC18F2510' , 0xFFE0 , 0x1F , 0x2000 , 4 , 0x8000 , 32  ],
		0x0CE0 : ['PIC18F2515' , 0xFFE0 , 0x1F , 0x4000 , 3 , 0xC000 , 64  ],
		0x1100 : ['PIC18F2520' , 0xFFF0 , 0x1F , 0x2000 , 4 , 0x8000 , 32  ],
		0x1110 : ['PIC18F2523' , 0xFFF0 , 0x1F , 0x2000 , 4 , 0x8000 , 32  ],
		0x0CC0 : ['PIC18F2525' , 0xFFE0 , 0x1F , 0x4000 , 3 , 0xC000 , 64  ],
		0x1240 : ['PIC18F2550' , 0xFFE0 , 0x1F , 0x2000 , 4 , 0x8000 , 32  ],
		0x2A40 : ['PIC18F2553' , 0xFFE0 , 0x1F , 0x2000 , 4 , 0x8000 , 32  ],
		0x1AC0 : ['PIC18F2580' , 0xFFE0 , 0x1F , 0x2000 , 4 , 0x8000 , 32  ],
		0x0EE0 : ['PIC18F2585' , 0xFFE0 , 0x1F , 0x4000 , 3 , 0xC000 , 64  ],
		0x0CA0 : ['PIC18F2610' , 0xFFE0 , 0x1F , 0x4000 , 4 , 0x10000 , 64 ],
		0x0C80 : ['PIC18F2620' , 0xFFE0 , 0x1F , 0x4000 , 4 , 0x10000 , 64 ],
		0x0EE0 : ['PIC18F2680' , 0xFFE0 , 0x1F , 0x4000 , 4 , 0x10000 , 64 ],
		0x2700 : ['PIC18F2682' , 0xFFE0 , 0x1F , 0x4000 , 5 , 0x14000 , 64 ],
		0x2720 : ['PIC18F2685' , 0xFFE0 , 0x1F , 0x4000 , 6 , 0x18000 , 64 ],
		0x2140 : ['PIC18F4221' , 0xFFE0 , 0x1F , 0x0800 , 2 , 0x1000 , 8   ],
		0x2100 : ['PIC18F4321' , 0xFFE0 , 0x1F , 0x1000 , 2 , 0x2000 , 8   ],
		0x10E0 : ['PIC18F4410' , 0xFFE0 , 0x1F , 0x2000 , 2 , 0x4000 , 32  ],
		0x10C0 : ['PIC18F4420' , 0xFFF0 , 0x1F , 0x2000 , 2 , 0x4000 , 32  ],
		0x10D0 : ['PIC18F4423' , 0xFFF0 , 0x1F , 0x2000 , 2 , 0x4000 , 32  ],
		0x2400 : ['PIC18F4450' , 0xFFE0 , 0x1F , 0x2000 , 2 , 0x4000 , 16  ],
		0x1220 : ['PIC18F4455' , 0xFFE0 , 0x1F , 0x2000 , 3 , 0x6000 , 32  ],
		0x2A20 : ['PIC18F4458' , 0xFFE0 , 0x1F , 0x2000 , 3 , 0x6000 , 32  ],
		0x1AA0 : ['PIC18F4480' , 0xFFE0 , 0x1F , 0x2000 , 2 , 0x4000 , 32  ],
		0x10A0 : ['PIC18F4510' , 0xFFE0 , 0x1F , 0x2000 , 4 , 0x8000 , 32  ],
		0x0C60 : ['PIC18F4515' , 0xFFE0 , 0x1F , 0x4000 , 3 , 0xC000 , 64  ],
		0x1080 : ['PIC18F4520' , 0xFFF0 , 0x1F , 0x2000 , 4 , 0x8000 , 32  ],
		0x1090 : ['PIC18F4523' , 0xFFF0 , 0x1F , 0x2000 , 4 , 0x8000 , 32  ],
		0x0C40 : ['PIC18F4525' , 0xFFE0 , 0x1F , 0x4000 , 3 , 0xC000 , 64  ],
		0x1200 : ['PIC18F4550' , 0xFFE0 , 0x1F , 0x2000 , 4 , 0x8000 , 32  ],
		0x2A00 : ['PIC18F4553' , 0xFFE0 , 0x1F , 0x2000 , 4 , 0x8000 , 32  ],
		0x1A80 : ['PIC18F4580' , 0xFFE0 , 0x1F , 0x2000 , 4 , 0x8000 , 32  ],
		0x0EA0 : ['PIC18F4585' , 0xFFE0 , 0x1F , 0x4000 , 3 , 0xC000 , 64  ],
		0x0C20 : ['PIC18F4610' , 0xFFE0 , 0x1F , 0x4000 , 4 , 0x10000 , 64 ],
		0x0C00 : ['PIC18F4620' , 0xFFE0 , 0x1F , 0x4000 , 4 , 0x10000 , 64 ],
		0x0E80 : ['PIC18F4680' , 0xFFE0 , 0x1F , 0x4000 , 4 , 0x10000 , 64 ],
		0x2740 : ['PIC18F4682' , 0xFFE0 , 0x1F , 0x4000 , 5 , 0x14000 , 64 ],
		0x2760 : ['PIC18F4685' , 0xFFE0 , 0x1F , 0x4000 , 6 , 0x18000 , 64 ]
             }

  PicFamily = 'PIC18F2XXX'
 

  def BulkErase(self):
    print "Bulk Erase ",
    #write 3F3FH to 3C0005H
    self.LoadMemoryAddress(0x3C0005)
    self.LoadCommandWord(self.C_PIC18_WRITE,0x3F3F)
    #write 8F8F to 3C0004H
    self.LoadMemoryAddress(0x3C0004)
    self.LoadCommandWord(self.C_PIC18_WRITE,0x8F8F)
    self.LoadCode(0)
    self.LoadCommand(self.C_PIC18_NOP)
    #wait 12 ms
    sleep(0.012)
    self.LoadWord(0)    
    #let's bulk erase eeprom data
    self.LoadMemoryAddress(0x3c0005)
    self.LoadCommandWord(self.C_PIC18_WRITE,0)
    self.LoadMemoryAddress(0x3c0004)
    self.LoadCommandWord(self.C_PIC18_WRITE,0x8484)
    self.LoadCode(0)
    self.LoadCommand(self.C_PIC18_NOP)
    sleep(0.012)
    self.LoadWord(0)
    print "..... Done!"



  def ProgramBurn(self, pic_data):
    print "Writing Program",
    print "Write buffer size =",self.WriteBufferSize
    #Direct access to code memory
    self.LoadCode(0x8EA6)
    self.LoadCode(0x9CA6)

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
      #Initiate write
      self.LoadCode(0x82A6)
      #Poll WR bit until bit is clear
      while True:
        #Poll WR bit,
        self.LoadCode(0x50A6)
        self.LoadCode(0x6EF5)
        self.LoadCommand(self.C_PIC18_TABLAT)
        EECON1 = self.ReadDataPic18()
        if (EECON1 & 2) == 0:
          break
# sleep maybe needed if using python compiler
      sleep(0.0001)

      #disable write
      self.LoadCode(0x94A6)
    print "Done!"





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


  ConfigMask= [0xCF3F, 0x1F3F, 0x8700, 0x00FD, 0xC03F, 0xE03F, 0x403F];


  def ConfigBurn(self,pic_data):
    print "CONFIG Burn",
    #burn all config but CONFIG6H last because of WRTC
    for l in range(11)+[12,13,11]:
      #direct access config memory
      self.LoadCode(0x8EA6)
      self.LoadCode(0x8CA6)
      #position program counter
      self.LoadCode(0xEF00)
      self.LoadCode(0xF800)
      #get Config target value
      TargetValue = pic_data.get(self.ConfigBase + l)
      if TargetValue == None:
        continue
      TargetValue = TargetValue | (TargetValue << 8)
      #Set Table Pointer 
      self.LoadMemoryAddress(self.ConfigBase+l)
      self.LoadCommandWord(self.C_PIC18_START_PGM,TargetValue)
      self.WriteAndWait()
    print " ... Done!"
    
   

  def ConfigCheck(self,pic_data):
    print "Config Check ",

#    config parameter too different from cpu to cpu
#    just skip it

    print "Skipped"
    return True




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
         self.WriteBufferSize = _cpuInfo[self.ListWriteBufferSize]
         return _cpuInfo 
    return  None



