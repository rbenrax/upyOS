
import time, sys, utls, sdata

def __main__(args):
    
    print (f"Prueba de llamada {args}")
    
    print(sys.modules)
    
    print(utls.human(12274))

    time.sleep(1)
    
    print(sdata.sysconfig)