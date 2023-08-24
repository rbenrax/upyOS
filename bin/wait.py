from utime import sleep
import sdata

def __main__(args):

    if len(args) < 1:
        print ("Usage: wait <seconds>")
        return

    sleep(int(float(args[0])))