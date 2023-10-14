import utime

# Proc ref pass in call
proc=None

def __main__(args):

    if len(args) == 0:
        print("Repeat a command every specified time\nUsage: watch <cmd> <args> -t <time>")
        return

    t=2.0
    
    if len(args) > 2 and args[-2] == "-t" and args[-1].isdigit():
        t=float(args[-1])
        cmd=" ".join(args[:-2])
    else:
        cmd=" ".join(args)
        
    while True:
        
        if proc.sts=="S":break
        
        if proc.sts=="H":
            utime.sleep(1)
            continue
        
        print(f"\033[2J\033[HEvery: {t}s: {cmd}")
        proc.syscall.run_cmd(cmd)
        utime.sleep(t)
        
        



        

        
