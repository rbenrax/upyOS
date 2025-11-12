
# ATmodem test program, use with an ESP-AT mcu capable (see /etc/modem.inf)

from esp_at import ModemManager
import time
import sdata

class ModemTest(ModemManager):
    def __init__(self, device):
        super().__init__(device)
         
    def callBack(self, cmd, resp):
#        pass
        print("**CB: " + cmd + " -> " + resp)
        
def __main__(args):

    # Create instancia mt
    mt = ModemTest("modem0")
    #mt.setCallBack(mt.callBack) # for trace AT commands
    
    # An other trace option
    #mt.sctrl = True
    #mt.scmds = True
    #mt.sresp = True
    #mt.timming = True
    
    # ... Or direct by program WIFI connection
    #mt.resetHW(22, 1)
    #if not mt.createUART(1, 115200, 4, 5, "modem0"):
    #    return
    
    #mt.set_mode(1)
    
    #mt.wifi_connect("SSID","PASSW")

    #print("- Test: "    + str(mt.test_modem()))
    #print("- Version: " + mt.get_version())
        
    #print("- Status: "  + mt.wifi_status())
    #print("- IP: "      + mt.get_ip_mac("ip"))
    #print("- MAC: "     + mt.get_ip_mac("mac"))
        
    #mt.set_ntp_server()
    #print("- NTP time: " + str(mt.set_datetime()))
    
    # TCP test

    #srv="httpcan.org"
    #srv="httpbin.org"
    srv="192.168.2.132"
    #srv="fmstream.org"
    get="/"

    srv= "raw.githubusercontent.com"
    get= "/rbenrax/upyOS/refs/heads/main/etc/upgrade2.inf"

    #sts, _ = mt.atCMD("AT+CIPSSLCCONF=0")
    #sts, _ = mt.atCMD("AT+CIPSNIREQ=0")
    
    print("Ping: " + mt.ping(srv))
    
    print("- Create TCP Connection")
    #mt.create_conn(srv, 8200, "TCP", keepalive=60)
    mt.create_conn(srv, 443, "SSL", keepalive=60)

    print("- Send request")
    req = f"GET {get} HTTP/1.1\r\nHost: {srv}\r\nUser-Agent: upyOS\r\nAccept: */*\r\n\r\n"
    
    #sts, ret = mt.send_data(req)
    sts, ret = mt.send_data_transp(req, 5)
    #print(f"- sts: {sts} / ret: {ret}")
    
    f = open('datos.txt', 'w')
    
    print("- Data receiving")
    #sts, data = mt.rcvDATA(0, True, 10, f)
    sts, body, headers = mt.rcvDATA(0, True, 15)
    if sts:
        print(body)
        f.write(body)
    else:
        print("- No Data")
    
    f.close()
    
    time.sleep(2)
    
    mt.close_conn() # if not closed by server
     
    #print("- Disconnecting ...")
    #mt.wifi_disconnect()

   