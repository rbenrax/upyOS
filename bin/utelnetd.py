import sys
import sdata

def __main__(args):

    if len(args) == 1 and args[0]=="--h":
        print ("utelnetserver")
        return

    import utelnetserver
    utelnetserver.start()
    del sys.modules["utelnetserver"]