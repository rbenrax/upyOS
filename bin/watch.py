import utime

# Proc ref pass in call
proc=None

def __main__(args):

    if len(args) == 0:
        print("Repeat command every time\nUsage: watch <cmd> <args> -t <every>")
        return

    t=2
    
    #TODO: change args get
    if len(args) > 2 and args[-2] == "-t":
        t=float(args[-1])
        cmd=args[:-2]
    else:
        cmd=args
        
    while True:
        print(f"\033[2J\033[HEvery: {t}\t{cmd}")
        proc.syscall.run_cmd(" ".join(cmd))
        utime.sleep(t)
        if proc.sts=="S":break


        

        
