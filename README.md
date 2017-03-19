burnLVP
=======

  Python code to program using the Raspberry Pi Microchip cpu like Pic12/16F and now PIC18F....


 
     The Python code

      - burnLVP.py      Original Python code use to program pic12F... and pic16F.....
      - burn18.py       Python code to program pic18F....  Please use burnLVPx.py instead
                      

      BurnLVPx          ( PIC12,16 and 18 family)

      - burnLVPx.py     Version to burn PIC12 and PIC18 Familly.
      - CpuPIC12.py	    PIC12 & PIC16 class
      - CpuPIC18F.py    PIC18 generic class
      - CpuPIC18FXX2    PIC18FXX2 class  (like  PIC18F258)
      - CpuPIC18F2XXX   PIC18F2XXX Class (like PIC18F2580)
      - CpuPIC18FXXK80  PIC18FXXK80 Class (like PIC18F26K80)
      - CpuPIC18F2_4XK22 PIC18F2_4XK22 Class thanks to Pascal Sandrez
      - burnGPIO.py     IO interface to quickly change type  of IO. (PC , USB, etc..)

     Schematic

      - RpiPgm.png      Original  schematic to program PIC12F1840 via Raspberry Pi GPIO .

P.S.  You will need python2.7 and intelhex modules


     For the chip cpu just follow these instructions
     
     sudo apt-get update
     sudo apt-get install git
     sudo apt-get install python
     sudo apt-get install python-dev python-pip
     sudo pip install intelhex
     git clone https://github.com/danjperron/burnLVP
     sudo apt-get install build-essential
     git clone git://github.com/xtacocorex/CHIP_IO.git
     
     And now you are able to program
     ex: 
      chip@chip:~$ git clone https://github.com/danjperron/RS485switch
      Clonage dans 'RS485switch'...
      remote: Counting objects: 18, done.
      remote: Total 18 (delta 0), reused 0 (delta 0), pack-reused 18
      Dépaquetage des objets: 100% (18/18), fait.
      Vérification de la connectivité... fait.
      chip@chip:~$ cd burnLVP
      chip@chip:~/burnLVP$ sudo python burnLVPx.py ~/RS485switch/rs485switch.hex 
      [sudo] password for chip: 
      C.H.I.P GPIO
      File " /home/chip/RS485switch/rs485switch.hex " loaded
      Scan CPU 
      Check PIC12/16...
      Cpu Id   = 0x0
      Revision =  0x4
      Found  PIC12F1840 from Cpu Family  PIC12/16
      Cpu Id: 0x1b80  revision: 4
      Bulk Erase Program , Data. .... done.
      Program blank check................................Passed!
      Data Blank check........Passed!
      Writing Program................................Done.
      Program check ................................Passed!
      Writing Data Done.
      Data check  Passed!
      Writing Config..Done.
      Config Check..Passed!
      Program verification passed!
      chip@chip:~/burnLVP$
