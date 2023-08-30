# Thread Test 
# From command line launch with & ending

#import sdata
import utime
import sdata

hd=None

def __th__(th):
    global hd 
    hd=th
    
def __main__(args):
    cont=0
    while True:
        cont+=1
        print(f"{hd} {sdata.getenv(hd)} Hola {cont} ")
        utime.sleep(4)
        if sdata.getenv(hd)!="R": break

if __name__ == "__main__":
    args =[""]
    __main__(args)
    
        