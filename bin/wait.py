from utime import sleep
import sdata

def __main__(args):

    if len(args) < 1:
        print ("Wait for for a process end\nUsage: wait <pid>")
        return

    sleep(0.200)
    while True:
        found=False
        for i in sdata.procs:
            if int(args[0]) == i.pid:
                found=True
        if found:
            sleep(0.200)
        else:
            break
