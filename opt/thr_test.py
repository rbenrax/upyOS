# Thread Test 
# From command line launch with & ending

import utime
from _thread import get_ident

# Current process refeference (passed in call)
proc=None

def __main__(args):
    #proc.syscall.run_cmd("ps")
    cont=0
    while True:
        cont+=1
        print(f"Hola {cont} ")
        utime.sleep(4)

        if proc.sts=="S":break

if __name__ == "__main__":
    args =[""]
    __main__(args)
    
        