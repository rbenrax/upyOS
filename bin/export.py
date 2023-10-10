import utls

def __main__(args):

#    if len(args) == 1:
#        args=args[0].split("=")

    if len(args) == 2:
        utls.setenv(args[0], args[1])
    else:
        print("Export env variable\nUsage: export <var>[=]<val>: var ?, 0, 1, $x ..., any")


