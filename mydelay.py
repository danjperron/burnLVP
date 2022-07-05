import ctypes, os

#use librt.so.1 to get time elapse in nanosecond
# only interested in 32bits nanosecond timer


#need to implement subtraction on ctype.ulong

class my_c_ulong(ctypes.c_ulong):
     def __sub__(self, other):
         return my_c_ulong(self.value - other.value)


class ttime(ctypes.Structure):
        _fields_ =\
        [
            ('sec', my_c_ulong),
            ('nanosec', my_c_ulong)
        ]
librt = ctypes.CDLL('librt.so.1', use_errno=True)
clock_gettime = librt.clock_gettime

_time1 =  ttime()
_time2 =  ttime()


#function to return after  microsecond increment
#only valid for <1second difference
def  nanoSleep(delay_nanos):
  if clock_gettime(4,ctypes.pointer(_time1)) !=0:
     return;
  startTime = _time1.nanosec
  while True:
      if clock_gettime(4,ctypes.pointer(_time2)) !=0:
         return;
      endTime = _time2.nanosec
      delta = (endTime-startTime).value
      if delta> delay_nanos:
          return


def mydelay():
  #PI4 and next  use microSleep
  #right now the minimum  sleep on Pi4 is ~15us but vary.
  #just assume that is higher than 5us
  nanoSleep(5000)
  #PIB or other  use  pass but change range
  #for i in range(5):
  #    pass 

