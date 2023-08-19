import sdata

def __main__(args):
    if len(args) == 1:
        val = sdata.getenv(args[0])
        print(val)
        return(val)
    else:
        print("Show env variable, echo <var>: var $?, $1, ..., any")


