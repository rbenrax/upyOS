import utls

def __main__(args):

    if len(args) == 0 or "--h" in args:
        print("Get or set gpio value\nUsage: gpio --h <gpio> [value] [>[>] <var>/<file>]")
    else:

        ret = 0
        from machine import Pin

        if len(args)==1:
            ret = Pin(int(args[0]), Pin.IN).value()
        else:
            ret=int(args[1])
            Pin(int(args[0]), Pin.OUT).value(ret)

        utls.outs(args, ret)
