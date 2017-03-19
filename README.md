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

 
     For Chip there is a modification to do in git://github.com/xtacocorex/CHIP_IO.git
     You need to unexport gpio before eport in the file  event_gpio.c in the source folder
    
 'int gpio_export(int gpio)
{
    int fd, len, e_no;
    char filename[MAX_FILENAME];
    char str_gpio[80];
    struct gpio_exp *new_gpio, *g;

    if (DEBUG)
        printf(" ** gpio_export **\n");

   // verify if it is already exported
   // if it is ! unexport firt
   // djp  March 18,2017
   snprintf(filename, sizeof(filename), "/sys/class/gpio/gpio%d", gpio);BUF2SMALL(filename);
   fd = open(filename,O_RDONLY);
   if(fd >=0)
   {
     close(fd);
     gpio_unexport(gpio);
   }
 ...
 '
