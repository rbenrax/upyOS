import sdata

def __main__(args):

    if len(args) == 2:
        sdata.setenv(args[0], args[1])
    else:
        print("Export env variable\nUsage: export <var> <val>: var $?, $1, ..., any")


