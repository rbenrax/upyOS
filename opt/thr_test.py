# Thread Test 
# From command line launch with & ending

import sdata
import utime
from _thread import get_ident

# The user space functions can avoid module being removed (passed in call)
rmmod=False

# The user space functions can call system funcions by syscall reference (passed in call)
syscall=None

def __main__(args):
    syscall.ps()
    cont=0
    while True:
        cont+=1
        print(f"Hola {cont} ")
        utime.sleep(4)

        if sdata.endthr(get_ident()): break

if __name__ == "__main__":
    args =[""]
    __main__(args)
    
        