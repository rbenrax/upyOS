# Thread Test 
# From command line launch with & ending

import sdata
import utime

def __main__(args):
    cont=0
    while True:
        cont+=1
        print(f"{sdata.getenv("THR1")} Hola {cont} ")
        utime.sleep(4)
        if sdata.getenv("THR1")!="R": break

if __name__ == "__main__":
    args =[""]
    __main__(args)
    
        