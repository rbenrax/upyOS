import sdata

def __main__(args):

    if len(args) == 1:
        sdata.unset(args[0])
    else:
        print("Remove env variable, unset <var>: var $?, $1, ..., any")



