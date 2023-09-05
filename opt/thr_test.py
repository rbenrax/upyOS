# Thread Test 
# From command line launch with & ending

import sdata
import utime
from _thread import get_ident

def __main__(args):
    cont=0
    while True:
        cont+=1
        print(f"Hola {cont} ")
        utime.sleep(4)

        if sdata.endthr(get_ident()): break

if __name__ == "__main__":
    args =[""]
    __main__(args)
    
        