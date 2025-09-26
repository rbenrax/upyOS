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

            def handlerFuncEdit(httpClient, httpResponse, routeArgs) :
              print("In EDIT HTTP variable route :")
              print(" - testid   = %s" % routeArgs['testid'])
              print(" - testpath = %s" % routeArgs['testpath'])
              
              httpResponse.WriteResponseOk(
                    headers=None,
                    contentType="text/html",
                    contentCharset="UTF-8",
                    content="Ok")

            def cmdGetHandler(httpClient, httpResponse) :
              #print(httpClient.GetRequestQueryString())
              formData = httpClient.GetRequestQueryParams()
              print(formData)
              cmd1 = formData['cmd1'].replace('+',' ')
              print("cmd1: " + cmd1)
              import sdata
              sdata.upyos.run_cmd(cmd1)
                          
              content   = """\
              <!DOCTYPE html>
              <html>
                <head>
                  <meta charset="UTF-8" />
                  <title>Test Comando get</title>
                </head>
                <body>
                  <h1>Comando ejecutado GET:</h1>
                  comando = %s<br />
                </body>
              </html>
              """ % (cmd1)
                     
              #print(content)
              httpResponse.WriteResponseOk(
                    headers=None,
                    contentType="text/html",
                    contentCharset="UTF-8",
                    content=content)

            def cmdPostHandler(httpClient, httpResponse) :
              formData = httpClient.ReadRequestPostedFormData()
              print(formData)
              #cmd2 = MicroWebSrv.HTMLEscape(formData["cmd2"])
              cmd2 = formData["cmd2"].replace('+',' ')
              print("cmd2: " + cmd2)
              
              import sdata
              sdata.upyos.run_cmd(cmd2)
              
              content   = """\
              <!DOCTYPE html>
              <html>
                <head>
                  <meta charset="UTF-8" />
                  <title>Test Comando POST</title>
                </head>
                <body>
                  <h1>Comando ejecutado Post:</h1>
                  comando = %s<br />
                </body>
              </html>
              """ % (cmd2)
             
              #print(content)
              httpResponse.WriteResponseOk( headers         = None,
                                            contentType     = "text/html",
                                            contentCharset  = "UTF-8",
                                            content         = content)

            routeHandlers = [
              ( "/edit/<testid>/<testpath>", "GET", handlerFuncEdit),
              ( "/runcmd1", "GET", cmdGetHandler),
              ( "/runcmd2", "POST", cmdPostHandler)
            ]
            
            mws = MicroWebSrv(proc, routeHandlers=routeHandlers, port=dport, bindIP='0.0.0.0', webPath="/www")
            mws.Start(threaded=False)

        elif args[0]=="stop":
            proc.syscall.run_cmd("killall uhttpd")
            
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

