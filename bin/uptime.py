import utime
import sdata
import utls

def __main__(args):
    
    if "--h" in args:
        print("Show uptime since last boot\nUsage: uptime [>[>] <var>/<file>]")
        return
    
    localt = utime.gmtime(utime.time())
    uptime_seconds = utime.time() - sdata.initime
    uptime_days = uptime_seconds // 86400
    uptime_seconds_remaining = uptime_seconds % 86400
    uptime_hms = utime.gmtime(uptime_seconds_remaining)
    
    ret = "{:0>2}:{:0>2}:{:0>2} up {} days, {:0>2}:{:0>2}:{:0>2}".format(
        localt[3], localt[4], localt[5], 
        uptime_days, uptime_hms[3], uptime_hms[4], uptime_hms[5]
    )
    
    utls.outs(args, ret)