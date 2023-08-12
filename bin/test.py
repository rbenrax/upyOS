
import time, sys, utls, sdata

def __main__(args):
    
    print (f"Prueba de llamada {args}")
    
    #print(sys.modules)

    #time.sleep(1)
    
    print(sdata.sysconfig)
    a={"a":1, "b":2, "c", 3}
    print(a)
    for key, value in a.items():
       if value == 2:
          print(key)
