proc=None

def __main__(args):

    if len(args) == 1:
        proc.syscall.unset(args[0])
    else:
        print("Unset env variable\nUsage: unset <var>")


