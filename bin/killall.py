import sdata
def __main__(args):
    pn=""
    if len(args) > 0:
        if args[0] == "--h" :
            print("Kill all process, or by name\nUsage: killall [process name/partial name]")
            return
        else:
            pn=args[0]

    sdata.upyos.killall(pn)
