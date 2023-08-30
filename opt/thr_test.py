# Thread Test 
# From command line launch with & ending

#import sdata
import utime

def __main__(args):
    cont=0
    while True:
        cont+=1
        print(f"Hola {cont}")
        utime.sleep(1)

if __name__ == "__main__":
    args =[""]
    __main__(args)
    
        