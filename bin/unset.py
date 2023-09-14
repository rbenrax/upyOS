proc=None

def __main__(args):

    if len(args) == 1:
        if args[0][0]=="$":
            args[0] = proc.syscall.getenv(args[0][1:])
        proc.syscall.unset(args[0])
    else:
        print("Unset env variable\nUsage: unset <var>")


