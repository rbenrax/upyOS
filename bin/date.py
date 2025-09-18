import utime
import utls

def __main__(args):

    if "--h" in args:
        print("Show current data and time (default) -d=date, -t=time [> <var>]")
        return
    
    ret=""
    localt = utime.gmtime(utime.time())
    if "-d" in args:
        ret = f"{localt[2]:0>2}/{utls.MONTH[localt[1]]}/{localt[0]:0>4}"
    elif "-t" in args:
        ret = f"{localt[3]:0>2}:{localt[4]:0>2}:{localt[5]:0>2}"
    else:
        ret = f"{utls.WEEKDAY[localt[6]]} {localt[2]:0>2}/{utls.MONTH[localt[1]]}/{localt[0]:0>4} {localt[3]:0>2}:{localt[4]:0>2}:{localt[5]:0>2}"
    
    if not utls.redir(args, ret):
        print(ret)
            
    
    