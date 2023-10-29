import sys

proc=None

def __main__(args):

    if len(args) == 1:

        import uftpdserver
        
        dport=21
        
        if args[0]=="start":
            print(f"Starting uftpd service on port {dport}")
            uftpdserver.start(port=dport, verbose=0)
            
        elif args[0]=="stop":
            uftpdserver.stop()
            del sys.modules["uftp"]

        elif args[0]=="restart":
            uftpdserver.restart()

        else:
            print("Invalid argument")
    else:
        print ("uftpd, uftpd <options>, start, stop, restart")

