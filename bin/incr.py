import utls

def __main__(args):

    if len(args) == 0:
        print("Increment a env variable\nUsage: incr <var> [<incr>]:")
        return
    
    val=0
    inc=1
    
    if len(args) > 0:
        if utls.getenv(args[0])=="":
            utls.setenv(args[0], 0)
            
        val = int(utls.getenv(args[0]))

    if len(args) == 2:
        inc=int(args[1])

    utls.setenv(args[0], str(val + inc))
