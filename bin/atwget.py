from esp_at import ModemManager
import time
import sys
import gc

#atwget https://github.com/rbenrax/upyOS/blob/main/media/ftpfs.py

def __main__(args):
    
    device = "modem0"
    if "-M" in args:
        idx = args.index("-M")
        if idx + 1 < len(args):
            device = args[idx+1]
            del args[idx:idx+2]
            
    if len(args) == 0:
        print ("Get a file from the net\nUsage:wget <url> [<size>] [-M <modem>]")
        return
    
    url = args[0]
    filename = ""
    
    if url.endswith("/"):
        filename = "index"
    else:
        filename = url.split("/")[-1].split("?")[0]
    
    size = 0
    if len(args) > 1:
        size = int(args[1])

    mm = ModemManager(device)
    #mm.sctrl = True
    #mm.scmds = True
    #mm.sresp = True
    #mm.timing = True

    try:
        
        if not mm.create_url_conn(url, keepalive=120):
            print("\nError: Cant connect")
            return
        
        mm.atCMD("ATE0") # Echo off
        mm.atCMD("AT+CIPMODE=1") # Transmissnon type 1
        mm.send_passthrough() # Send for passthrough
        
        gc.collect()
        sts = mm.http_get_to_file_t(url, filename, sz=size)
        if not sts:
            print(f"\nError downloading {filename}")
    
    except Exception as ex:
        print(f"atwget: {filename} - {str(ex)}")
        sys.print_exception(ex)
    
    finally:
        if mm and mm.modem: 
            try:
                time.sleep(1)
                mm.modem.write("+++")
                time.sleep(1)
                mm.atCMD("AT+CIPMODE=0", 3)
                if mm.tcp_conn:
                    mm.close_conn()  
                mm.atCMD("ATE1", 2)
            except:
                pass