import sys
import sdata

def __main__(args):

    from microWebSrv import MicroWebSrv



    if len(args) == 1:
        from microWebSrv import MicroWebSrv

        if args[0]=="start":
            from microWebSrv import MicroWebSrv
            
            mws = MicroWebSrv(routeHandlers=[], port=80, bindIP='0.0.0.0', webPath="/www")
            mws.Start(threaded=True)
            
            #sdata.httpd = MicroWebSrv()      # TCP port 80 and files in /flash/www
            #sdata.httpd.Start(threaded=True) # Starts server in a new thread
            
            #sdata.httpd = MicroWebSrv(routeHandlers=None, port=80, bindIP='0.0.0.0', webPath="/flash/www")
            #sdata.httpd.Start(threaded=True)
        #elif args[0]=="stop":
            #sdata.httpd.stop()
        #elif args[0]=="status":
            #print("uhttpd status: " + sdata.httpd.IsStarted())
        else:
            print("Invalid argument")
    else:
        print ("MicroWebSrv, uhttpd <options>, start, stop")

