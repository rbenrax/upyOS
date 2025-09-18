import utls

def __main__(args):

    args = [a for a in args if a != "="]

    if len(args) == 2:
        utls.setenv(args[0], args[1])
    elif len(args) == 3:
        if args[2] == '-i':
            utls.setenv(args[0], int(args[1]))
        elif args[2] == '-f':
            utls.setenv(args[0], float(args[1]))
        elif args[2] == '-b':
            if args[1].lower() == "True"':
                utls.setenv(args[0], True)
            else:
                utls.setenv(args[0], False)
        else:
            utls.setenv(args[0], args[1])
    else:
        print("Export env variable\nUsage: export <var>[=]<val> [-i=int, -f=float, -s=string, -b=bool]: var ?, 0, 1, $x ..., any")
