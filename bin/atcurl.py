from esp_at import ModemManager
import utls
import time
import sys

def __main__(args):
    doc = """
    atcurl - Basic curl-like command for MicroPython
    Usage: atcurl [OPTIONS] <URL> [>[>]] var/file
    
    Options:
      -X, METHOD  HTTP method (GET, POST, PUT, DELETE). Default: GET
      -H, HEADER  Add HTTP header (e.g., "Content-Type: application/json")
      -d, DATA    Data to send in body (for POST/PUT)
      -i,         Show response headers
      -v,         Verbose mode
      --h         Show this help
    """
    
    if len(args) == 0 or "--h" in args:
        print(doc)
        return
    
    # Default values
    method = "GET"
    headers = []
    data = None
    show_response_headers = False
    verbose = False
    url = None
    
    # Parse arguments
    i = 0
    while i < len(args):
        arg = args[i]
        
        if ">" in arg: break
        
        if arg in ["-X"]:
            if i + 1 < len(args):
                method = args[i + 1].upper()
                i += 2
            else:
                print("Error: -X requires a method")
                return
                
        elif arg in ["-H"]:
            if i + 1 < len(args):
                headers.append(args[i + 1])
                i += 2
            else:
                print("Error: -H requires a header")
                return
                
        elif arg in ["-d"]:
            if i + 1 < len(args):
                data = args[i + 1]
                i += 2
            else:
                print("Error: -d requires data")
                return
                
        elif arg in ["-i"]:
            show_response_headers = True
            i += 1
            
        elif arg in ["-v"]:
            verbose = True
            i += 1
            
        elif not arg.startswith("-"):
            url = arg
            i += 1
            
        else:
            print(f"Error: Unknown option: {arg}")
            return
    
    if not url:
        print("Error: URL required")
        print("Usage: atcurl [OPTIONS] <URL>")
        return
    
    # Validate method
    valid_methods = ["GET", "POST", "PUT", "DELETE", "HEAD", "PATCH"]
    if method not in valid_methods:
        print(f"Error: Invalid method '{method}'. Use: {', '.join(valid_methods)}")
        return
    
    # Process URL
    try:
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
            
        parts = url.split('/', 3)
        if len(parts) < 4:
            hostport = parts[2] if len(parts) > 2 else parts[0]
            path = "/"
        else:
            _, _, hostport, path = parts
            
        tmp = hostport.split(':')
        host = tmp[0]
        port = int(tmp[1]) if len(tmp) > 1 else 80
        
        if not path.startswith("/"):
            path = "/" + path
            
    except Exception as e:
        print(f"Error: Bad URL - {str(e)}")
        return
    
    # Setup modem
    mm = ModemManager("modem0")
    
    # Enable debugging if verbose
    if verbose:
        mm.sctrl = True
        mm.scmds = True
        mm.sresp = True
        mm.timing = True
    
    try:
        # Create connection
        if verbose:
            print(f"Connecting to {host}:{port}...")
            
        if not mm.create_url_conn(url, keepalive=20):
            print("Error: Cannot connect to server")
            return
        
        # Build request
        content_length = f"Content-Length: {len(data)}\r\n" if data else ""
        
        req = (f"{method} {path} HTTP/1.1\r\n"
               f"Host: {host}\r\n"
               f"User-Agent: upyOS-curl/1.0\r\n"
               f"Accept: */*\r\n"
               f"{content_length}")
        
        # Add custom headers
        for header in headers:
            req += f"{header}\r\n"
        
        # Add data if exists
        if data:
            req += f"\r\n{data}"
        else:
            req += "\r\n"
        
        if verbose or mm.scmds:
            print("=== REQUEST ===")
            print(req)
            print("===============")
        
        # Send request
        sts, ret = mm.send_data(req, 5)
        if not sts:
            print("Error: Cannot send request")
            return
        
        # Receive response
        if verbose:
            print("Waiting for response...")
        
        sts, body, headers = mm.rcv_data(0, True, 15)
        
        if sts:
            ret=""
            if show_response_headers:
                #print(headers)
                ret+=headers
            #print(body)
            ret+=body
            utls.outs(args, ret)
        else:
            print("Error: No response from server")
    
    except Exception as ex:
        print(f"Error: {str(ex)}")
        if verbose:
            sys.print_exception(ex)
    
    finally:
        # Close connection
        if mm.tcp_conn:
            mm.close_conn()

# Usage examples:
# atcurl "http://httpbin.org/get"
# atcurl -X POST -H "Content-Type: application/json" -d '{"key":"value"}' http://httpbin.org/post
# atcurl -i -v https://api.github.com/users/octocat