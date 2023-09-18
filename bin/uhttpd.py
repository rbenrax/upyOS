import sys
import sdata

proc=None

def __main__(args):
    
    #./uhttpd start &
    
    from microWebSrv import MicroWebSrv
    
    mws = MicroWebSrv(proc, routeHandlers=[], port=80, bindIP='0.0.0.0', webPath="/www")
    mws.Start(threaded=False)
    
    #sdata.httpd = MicroWebSrv()      # TCP port 80 and files in /flash/www
    #sdata.httpd.Start(threaded=True) # Starts server in a new thread
    
    #sdata.httpd = MicroWebSrv(routeHandlers=None, port=80, bindIP='0.0.0.0', webPath="/flash/www")
    #sdata.httpd.Start(threaded=True)


