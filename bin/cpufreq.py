import sdata
import utls
from machine import freq

def __main__(args):

    if "--h" in args or len(args) == 0:
        print("Set clock speed\nUsage: cpuclock <option>: <freq> (caution), --h -v [>[>] <var>/<file>]")
        return

    if args[0] == "-v":
        ls = f"CPU speed: {freq()*0.000001} MHz"
        utls.outs(args, ls)
        return
        
    if args[0].isdigit():
        f = int(args[0])
    else:
        print("Invalid argument")
        return
    
    try:
        freq(f * 1000000)
        ls = "CPU speed set to " + str(f) + " Mhz"
        utls.outs(args, ls)
        
    except ValueError as ve:
        print(ve)
        
        

        
