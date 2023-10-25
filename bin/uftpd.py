import sys
import sdata

proc=None

def __main__(args):

    if len(args) == 1:
        #import ftptiny
        #ftp = ftptiny.FtpTiny()
        import ftp
        
        if args[0]=="start":
            #ftp.start()
            while not proc.sts=="S":
                ftp.ftpserver(proc, port=21, timeout=None)
                
        elif args[0]=="stop":
            #ftp.stop()
            #del sys.modules["ftptiny"]
            proc.syscall.run_cmd("killall uftpd")
            
            #False connection to close de thread
            import socket
            sock = socket.socket()
            sock.connect(("127.0.0.1", 21))
            sock.close()
            del sys.modules["ftp"]

        else:
            print("Invalid argument")
    else:
        print ("ftptiny, uftpd <options>, start, stop")

