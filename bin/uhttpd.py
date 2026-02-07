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
            _upyDesktop = None
            try:
                import upyDesktop
                _upyDesktop = upyDesktop
                routeHandlers += upyDesktop.routes
            except ImportError:
                print("Could not import upyDesktop")
            
            mws = MicroWebSrv(proc, routeHandlers=routeHandlers, port=dport, bindIP='0.0.0.0', webPath="/www")
            
            # Hook Terminal WebSocket
            if _upyDesktop and hasattr(_upyDesktop, 'ws_accept_callback'):
                 mws.AcceptWebSocketCallback = _upyDesktop.ws_accept_callback
                 
            mws.Start(threaded=True)

        elif args[0]=="stop":
            sdata.upyos.run_cmd("killall uhttpd")
            
            try:
                del sys.modules["upyDesktop"]
                del sys.modules["microWebSocket"]
                del sys.modules["microWebTemplate"]
                del sys.modules["microWebSrv"]
            except:
                pass
            
        else:
            print("Invalid argument")
    else:
        print ("uhttpd, uhttpd <options>, start, stop")

