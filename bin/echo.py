import utls

# This command allows you to redirect the output to an environment variable.
# Afterwards, it is possible to send it to a file using the 'touch' command: "touch <filename> <var, ...>"

def __main__(args):
    if len(args) > 0:
        if ">" in args:
            try:
                r = args.index(">")
                utls.setenv(args[r+1], "".join(args[:r]))
            except IndexError:
                print("Error: falta el nombre de la variable destino después de '>'")
        else:
            print("".join(args))
    else:
        print("Show msg + env variable\nUsage: echo const/<var> [> <var>]")