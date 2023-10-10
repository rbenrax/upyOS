import utls

def __main__(args):

    if len(args) > 0:
        for a in args:
            utls.unset(a)
    else:
        print("Unset env variable\nUsage: unset <var> ...")


