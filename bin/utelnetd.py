import sys
import sdata

def __main__(args):

    if len(args) == 1:
        import utelnetserver
        
        if args[0]=="start":
            print(f"Starting telnetd service")
            utelnetserver.start()
        elif args[0]=="stop":
            utelnetserver.stop()
            del sys.modules["utelnetserver"]
        else:
            print("Invalid argument")
    else:
        print ("utelnetserver, utelnetd <options>, start, stop")

