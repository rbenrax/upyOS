import utls

def __main__(args):

    if len(args) == 0:
        print("Decrement a env variable\nUsage: decr <var> [<decr>]:")
        return
    
    val=0
    dec=1
    
    if len(args) > 0:
        if utls.getenv(args[0])=="":
            utls.setenv(args[0], 0)
            
        val = int(utls.getenv(args[0]))

    if len(args) == 2:
        inc=int(args[1])

    utls.setenv(args[0], str(val - dec))
