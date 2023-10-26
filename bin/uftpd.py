import sys
import sdata

proc=None

def __main__(args):

    if len(args) == 1:
        #import ftptiny
        #ftp = ftptiny.FtpTiny()
        import ftp
        
        dport=21
        if args[0]=="start":
            #ftp.start()
            print(f"Starting ftpd service on port {dport}")
            while not proc.sts=="S":
                ftp.ftpserver(proc, port=dport, timeout=None)
                
        elif args[0]=="stop":
            #ftp.stop()
            #del sys.modules["ftptiny"]
            proc.syscall.run_cmd("killall uftpd")
            
            #False connection to close de thread
            import socket
            sock = socket.socket()
            sock.connect(("127.0.0.1", dport))
            sock.close()
            del sys.modules["ftp"]

        else:
            print("Invalid argument")
    else:
        print ("ftptiny, uftpd <options>, start, stop")

