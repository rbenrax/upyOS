from utime import sleep
import sdata

def __main__(args):

    if len(args) == 0:
        print ("Wait for a process to finish\nUsage: wait <pid>")
        return

    sleep(0.100)
    while True:
        found=False
        for i in sdata.procs:
            if int(args[0]) == i.pid:
                found=True
        if found:
            sleep(0.200)
        else:
            break
