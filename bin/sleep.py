from utime import sleep
import sdata

def __main__(args):

    if len(args) < 1:
        print ("Wait for a while\nUsage: sleep <seconds>")
        return

    sleep(int(float(args[0])))