import utls

def __main__(args):

#    if len(args) == 1:
#        args=args[0].split("=")

    if len(args) == 2:
        utls.setenv(args[0], args[1])
    elif len(args) == 3:
        if args[2] == 'i':  # Corregido: args[1] -> args[2]
            utls.setenv(args[0], int(args[1]))  # Corregido: orden de parámetros
        elif args[2] == 'f':  # Corregido: args[1] -> args[2]
            utls.setenv(args[0], float(args[1]))  # Corregido: orden de parámetros
        else:
            utls.setenv(args[0], args[1])
    else:
        print("Export env variable\nUsage: export <var>[=]<val> [i=int, f=float, s=string]: var ?, 0, 1, $x ..., any")

