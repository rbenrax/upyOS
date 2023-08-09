import time
import sdata

def __main__(args):

    if len(args) < 1:
        print ("Usage: wait <seconds>")
        return

    time.sleep(int(args[0]))