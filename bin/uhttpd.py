import sys
import sdata

proc=None

def __main__(args):
    
    #uhttpd start &
    if len(args) == 1:
        from microWebSrv import MicroWebSrv

        if args[0]=="start":
            mws = MicroWebSrv(proc, routeHandlers=[], port=80, bindIP='0.0.0.0', webPath="/www")
            mws.Start(threaded=False)
            
            #sdata.httpd = MicroWebSrv()      # TCP port 80 and files in /flash/www
            #sdata.httpd.Start(threaded=True) # Starts server in a new thread
            
            #sdata.httpd = MicroWebSrv(routeHandlers=None, port=80, bindIP='0.0.0.0', webPath="/flash/www")
            #sdata.httpd.Start(threaded=True)

        elif args[0]=="stop":
            proc.syscall.run_cmd("killall uhttpd")
            proc.syscall.run_cmd("wget http://localhost:80/")
            del sys.modules["microWebSrv"]
            del sys.modules["urequests"]
            del sys.modules["usocket"]
        else:
            print("Invalid argument")
    else:
        print ("uhttpd, uhttpd <options>, start, stop")

