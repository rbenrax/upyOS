import machine
import sys

proc=None

def __main__(args):
    
    if "utelnetserver" in sys.modules: # avoid exit
        print("Can not reboot while telnet service is running, stop it or use reset instead")
        return
    else:
        proc.syscall.run_cmd("exit -r")
