import sys
import sdata

proc=None

def __main__(args):
    
    #uhttpd start &
    dport=80
    if len(args) == 1:
        from microWebSrv import MicroWebSrv

        if args[0]=="start":
            print(f"Starting httpd service on port {dport}")

            routeHandlers = []
            try:
                import upyDesktop
                routeHandlers += upyDesktop.routes
            except ImportError:
                print("Could not import upyDesktop")
            
            mws = MicroWebSrv(proc, routeHandlers=routeHandlers, port=dport, bindIP='0.0.0.0', webPath="/www")
            mws.Start(threaded=False)

        elif args[0]=="stop":
            sdata.upyos.run_cmd("killall uhttpd")
            
            import usocket
            sock = usocket.socket()
            sock.connect(("127.0.0.1", dport))
            sock.close()
            
            try:
                del sys.modules["microWebSrv"]
                del sys.modules["microWebTemplate"]
            except:
                pass
            
        else:
            print("Invalid argument")
    else:
        print ("uhttpd, uhttpd <options>, start, stop")

