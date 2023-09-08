import kernel
import utime

def __main__(args):

    print("This command should be analized, caos")
    return

    if len(args) == 0:
        print("Kill process\nUsage: kill <pid>")
        return
    
    # Kill process
    for i in kernel.procs:
        if i.pid == int(args[0]):
            i.sts="S"
            utime.sleep(.2)
            break
