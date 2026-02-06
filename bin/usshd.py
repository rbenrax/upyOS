import sys
import sdata

def __main__(args):

    if len(args) == 1:
        import usshserver
        
        if args[0]=="start":
            print(f"Starting Secure Telnet (SSH-like) service")
            usshserver.start()
        elif args[0]=="stop":
            usshserver.stop()
            del sys.modules["usshserver"]
        else:
            print("Invalid argument")
    else:
        print ("usshserver, usshd <options>, start, stop")
