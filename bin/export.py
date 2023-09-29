proc=None

def __main__(args):

#    if len(args) == 1:
#        args=args[0].split("=")

    if len(args) == 2:
#        if args[0][0]=="$":
#            args[0] = proc.syscall.getenv(args[0][1:])
#        if args[1][0]=="$":
#            args[1] = proc.syscall.getenv(args[1][1:])
        proc.syscall.setenv(args[0], args[1])
    else:
        print("Export env variable\nUsage: export <var>[=]<val>: var ?, 0, 1, $x ..., any")


