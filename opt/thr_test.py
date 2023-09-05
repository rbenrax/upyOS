# Thread Test 
# From command line launch with & ending

import sdata
import utime
import _thread

def __main__(args):
    cont=0
    while True:
        cont+=1
        print(f"Hola {cont} ")
        utime.sleep(4)

        pid_sts="R"
        thid = _thread.get_ident()
        for i in sdata.procs:
            if isinstance(i, str): continue
            print(f"{i.pid} {i.tid} {i.cmd} {i.args}")
            if i.tid == thid:
                pid_sts=i.sts
                break
                
        if pid_sts != "R": break

if __name__ == "__main__":
    args =[""]
    __main__(args)
    
        