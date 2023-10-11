import utls
import sdata

def __main__(args):

    if len(args) == 0:
        print("Decrement an env variable\nUsage: decr <var> [<decr>]:")
        return
    
    val=0
    dec=1
    
    if len(args) > 0:
        
        if not args[0] in sdata.sysconfig["env"]:
            utls.setenv(args[0], "0")
            
        tmp = utls.getenv(args[0])
        
        if tmp.lstrip("-").isdigit():
            val = int(tmp)
        else:
            print(f"Variable {args[0]} is not numeric")
            return

    if len(args) == 2:
        if args[1].isdigit():
            dec=int(args[1])

    utls.setenv(args[0], str(val - dec))
