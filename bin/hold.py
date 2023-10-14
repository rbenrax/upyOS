import sdata

def __main__(args):

    pid="0"
        
    if len(args) > 0:
        if args[0] == "--h":
            print("Hold a process by pid, if process is holdable: hold <pid>")
            return
        else:
            pid=args[0]

        for i in sdata.procs:
            if pid.isdigit() and i.pid == int(pid):
                i.sts="H"
                break