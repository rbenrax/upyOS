import utls
import sdata

def __main__(args):

    if len(args) == 0:
        print("Increase an env variable\nUsage: incr <var> [<incr>]:")
        return
    
    val=0
    inc=1
    
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
            inc=int(args[1])

    utls.setenv(args[0], str(val + inc))
