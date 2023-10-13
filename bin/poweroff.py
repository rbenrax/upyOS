import sys
import utime

import sdata

proc=None

def __main__(args):

    if len(args) == 1 and args[0] == "--h" :
        print("Stop upyOS\nUsage: poweroff")
        return
    else:

        if not sdata.debug:
            s=input("\nStop upyOS S/[N] : ")
            if s.upper()!="S": return

        # Stop threads before exit
        if len(sdata.procs)>0:
            print("\nStoping process...")
            
            proc.syscall.killall("")
            #self.killall("")
            while True:
                end=True
                for p in sdata.procs:
                    if p.isthr: end=False
                if end: break
                utime.sleep(.5)

        proc.syscall.print_msg("Shutdown upyOS..., bye.")
        print("")

        #raise SystemExit
        sys.exit()
