import utime
import sdata
import utls

def __main__(args):
    
    if "--h" in args:
        print("Show uptime since last boot\nUsage: uptime [>[>] <var>/<file>]")
        return
    
    localt = utime.gmtime(utime.time())
    uptime = utime.gmtime(utime.time() - (sdata.initime))
    
    ret = f"{localt[3]:0>2}:{localt[4]:0>2}:{localt[5]:0>2} {uptime[7]-1:3} days {uptime[3]:0>2}:{uptime[4]:0>2}:{uptime[5]:0>2} up"
    
    utls.outs(args, ret)