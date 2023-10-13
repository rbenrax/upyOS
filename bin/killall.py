import sdata

proc=None

def __main__(args):

    pn=""
        
    if len(args) > 0:
        if args[0] == "--h" :
            print("Kill all process, or by name\nUsage: killall [process name/partial name]")
            return
        else:
            pn=args[0]

    proc.syscall.killall(pn)
        
    #for i in sdata.procs:
    #    if pn in i.cmd:
    #        i.sts="S"
