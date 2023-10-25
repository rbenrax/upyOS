import sys
import sdata

def __main__(args):

    if len(args) == 1:
        import ftptiny
        ftp = ftptiny.FtpTiny()
        
        if args[0]=="start":
            ftp.start()
        elif args[0]=="stop":
            ftp.stop()
            del sys.modules["ftptiny"]
        else:
            print("Invalid argument")
    else:
        print ("ftptiny, uftpd <options>, start, stop")

