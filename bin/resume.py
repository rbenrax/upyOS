import sdata

def __main__(args):

    pid="0"
        
    if len(args) > 0:
        if args[0] == "--h":
            print("Resume a suspended process by pid, if process is holdable: resume <pid>")
            return
        else:
            pid=args[0]

        for i in sdata.procs:
            if pid.isdigit() and i.pid == int(pid):
                i.sts="R"
                break