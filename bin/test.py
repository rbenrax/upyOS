import utls
import sdata

def __main__(args):

    if len(args) == 0 or "--h" in args:
        print("Check if file/directory/proc/gpio exists/value\nUsage: test --h -p <proccess name> -f/-d <path> -g <gpio> [>[>] <var>/<file>]")
    else:

        ret = False
        if "-f" in args:
            idx = args.index("-f")
            if idx + 1 < len(args):
                ret = utls.file_exists(args[idx + 1])
            else:
                print("test: missing argument after -f")
                return

        if "-d" in args:
            idx = args.index("-d")
            if idx + 1 < len(args):
                ret = utls.isdir(args[idx + 1])
            else:
                print("test: missing argument after -d")
                return

        if "-p" in args:
            idx = args.index("-p")
            if idx + 1 < len(args):
                pn = args[idx + 1]
                for i in sdata.procs:
                    if pn in i.cmd:
                        ret=True
                        break
            else:
                print("test: missing argument after -p")
                return

        if "-g" in args:
            idx = args.index("-g")
            if idx + 1 < len(args):
                from machine import Pin            
                v = Pin(int(args[idx + 1]), Pin.IN).value()
                ret = True if v == 1 else False
            else:
                print("test: missing argument after -g")
                return

        utls.outs(args, ret)
