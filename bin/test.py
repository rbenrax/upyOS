import utls
import sdata

def __main__(args):

    if len(args) == 0 or "--h" in args:
        print("Check if file/directory/proc exists\nUsage: test --h -p <proccess name> -f/-d <path> [>[>] <var>/<file>]")
    else:

        ret = False
        if "-f" in args:
            ret = utls.file_exists(args[1])

        if "-d" in args:
            ret = utls.isdir(args[1])

        if "-p" in args:
            pn = args[1]
            for i in sdata.procs:
                if pn in i.cmd:
                    ret=True
                    break

        if "-g" in args:
            from machine import Pin            
            v = Pin(int(args[1]), Pin.IN).value()
            ret = True if v == 1 else False 

        utls.outs(args, ret)
