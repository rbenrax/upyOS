from esp_at import ModemManager
import time
import sys

#atwget https://github.com/rbenrax/upyOS/blob/main/media/ftpfs.py

def __main__(args):
    
    if len(args) == 0:
        print ("Get a file from the net\nUsage:wget <url>")
        return
    
    url = args[0]
    filename = ""
    
    if url.endswith("/"):
        filename = "index"
    else:
        filename = url.split("/")[-1].split("?")[0]

    mm = ModemManager("modem0")
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
        
        sts = mm.http_get_to_file_t(url, filename)
        if not sts:
            print(f"\nError downloading {filename}")
    
        if mm.tcp_conn: 
            time.sleep(1)
            mm.modem.write("+++")
            time.sleep(1)
            mm.atCMD("AT+CIPMODE=0", 3)
            
            mm.close_conn()  
            mm.atCMD("ATE1", 2)   
    except Exception as ex:
        print(f"atwget: {filename} - {str(ex)}")
        sys.print_exception(ex)