
# Sample HTTP manager, to use with an ESP-AT mcu capable with AT+http funcions, ej, esp32c3 (see /etc/modem.inf) 

from ATmodem import ModemManager
import time

class HttpManager(ModemManager):
    
    def __init__(self, device="modem0"):
        super().__init__(device)
        
        self.debug = False
        
def __main__(args):
 
    hm = HttpManager()
 
    if not hm.modem:
        
        print("- Connecting ...")
        hm.executeScript("/local/dial.inf") # Script connection
        
        # Alternative by program WIFI connection
        #hm.resetHW(22, 2)
        #if not hm.createUART(1, 115200, 4, 5, "modem0"):
        #    return

        #ret = hm.wifi_status()
        #if ret == 0:
        #    print("Conectando WIFI en htest ...")
        #    hm.set_mode(1)
        #    hm.wifi_connect("DIGIFIBRA-dDsK-E","")
            
        time.sleep(2)
        
        #print("Test: "     + str(hm.test_modem()))
        #print("Version: "  + hm.get_version())
    print("Local IP: " + hm.get_ip_mac("ip"))
        #print("MAC: "      + hm.get_ip_mac("mac"))

        #print(hm.set_ntp_server())
        #time.sleep(5)
        #print(hm.set_datetime())

# ---------
    # HTTP CMDs
    #+CMD:106,"AT+HTTPCLIENT",0,0,1,0
    #+CMD:107,"AT+HTTPGETSIZE",0,0,1,0
    #+CMD:108,"AT+HTTPURLCFG",0,1,1,0
    #+CMD:109,"AT+HTTPCHEAD",0,1,1,0
    #+CMD:110,"AT+HTTPCGET",0,0,1,0
    #+CMD:111,"AT+HTTPCPOST",0,0,1,0
    #+CMD:112,"AT+HTTPCPUT",0,0,1,0
    #+CMD:113,"AT+HTTPCFG",0,0,1,0

    #hm.scmds=True
    #hm.sresp=True
 
    time.sleep(2)
 
    # AT+HTTPCLIENT=1,0,"http://httpbin.org/get","httpbin.org","/get",1
    cmd = f'AT+HTTPCLIENT=1,0,"https://httpcan.org","httpcan.org","/get",1'
    #print(cmd)
    sts, resp = hm.atCMD(cmd, 10)
    print(f'Resp:{sts}\n{resp}')

