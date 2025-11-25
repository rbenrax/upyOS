import urequests
import sys
import utls

def __main__(args):
    doc = """
    atcurl - Basic curl-like command for MicroPython (ESP32)
    Usage: atcurl [OPTIONS] <URL>

    Options:
      -X METHOD   HTTP method (GET, POST, PUT, DELETE, HEAD, PATCH). Default: GET
      -H HEADER   Add HTTP header (e.g., "Content-Type: application/json")
      -d DATA     Data to send in body (for POST/PUT)
      -i          Include response headers in output
      -v          Verbose mode (show request info)
      --h         Show this help
    """
    
    if len(args) == 0 or "--h" in args:
        print(doc)
        return

    # Default values
    method = "GET"
    headers = {}
    data = None
    show_response_headers = False
    verbose = False
    url = None

    # Parse arguments
    i = 0
    while i < len(args):
        arg = args[i]
        
        if ">" in arg or ">>" in arg: break
        
        if arg == "-X":
            if i + 1 < len(args):
                method = args[i + 1].upper()
                i += 2
            else:
                print("Error: -X requires a method")
                return
                
        elif arg == "-H":
            if i + 1 < len(args):
                hdr = args[i + 1]
                if ": " in hdr:
                    key, val = hdr.split(": ", 1)
                elif ":" in hdr:
                    key, val = hdr.split(":", 1)
                    val = val.lstrip()
                else:
                    print("Error: Invalid header format. Use 'Key: Value'")
                    return
                headers[key] = val
                i += 2
            else:
                print("Error: -H requires a header")
                return
                
        elif arg == "-d":
            if i + 1 < len(args):
                data = args[i + 1]
                i += 2
            else:
                print("Error: -d requires data")
                return
                
        elif arg == "-i":
            show_response_headers = True
            i += 1
            
        elif arg == "-v":
            verbose = True
            i += 1
            
        elif not arg.startswith("-"):
            if url is not None:
                print("Error: Only one URL allowed")
                return
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
    valid_methods = {"GET", "POST", "PUT", "DELETE", "HEAD", "PATCH"}
    if method not in valid_methods:
        print(f"Error: Invalid method '{method}'. Use: {', '.join(valid_methods)}")
        return

    # Ensure URL has protocol
    if not url.startswith(("http://", "https://")):
        url = "http://" + url

    # Set default headers
    if "User-Agent" not in headers:
        headers["User-Agent"] = "MicroPython-atcurl/1.0"
    if "Accept" not in headers:
        headers["Accept"] = "*/*"

    # Verbose output
    if verbose:
        print(f"Method: {method}")
        print(f"URL: {url}")
        print("Headers:")
        for k, v in headers.items():
            print(f"  {k}: {v}")
        if data is not None:
            print(f"Body: {data}")

    try:
        # Perform request
        if method == "GET":
            resp = urequests.get(url, headers=headers)
        elif method == "POST":
            resp = urequests.post(url, data=data, headers=headers)
        elif method == "PUT":
            resp = urequests.put(url, data=data, headers=headers)
        elif method == "DELETE":
            resp = urequests.delete(url, headers=headers)
        elif method == "HEAD":
            resp = urequests.head(url, headers=headers)
        elif method == "PATCH":
            resp = urequests.patch(url, data=data, headers=headers)
        else:
            print(f"Error: Unsupported method {method}")
            return

        # Output
        output = ""
        
        if show_response_headers:
            # Format headers as string (like HTTP response)
            status_line = f"HTTP/1.1 {resp.status_code} {resp.reason.decode() if isinstance(resp.reason, bytes) else resp.reason}"
            output += status_line + "\r\n"
            for key, val in resp.headers.items():
                output += f"{key}: {val}\r\n"
            output += "\r\n"
        
        # Add body (text only; urequests.text handles decoding)
        output += resp.text
        
        #print(output, end="")
        utls.outs(args, output)

        resp.close()

    except Exception as ex:
        print(f"Error: {ex}")
        if verbose:
            sys.print_exception(ex)