
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
    #mt.scmds = True
    #mt.sctrl = True
    #mt.sresp = True
    #mt.timming = True
    
    # ... Or direct by program WIFI connection
    #mt.resetHW(22, 1)
    #if not mt.createUART(1, 115200, 4, 5, "modem0"):
    #    return
    
    #mt.set_mode(1)
    
    #mt.wifi_connect("SSID","PASSW")

    print("- Test: "    + str(mt.test_modem()))
    print("- Version: " + mt.get_version())
        
    print("- Status: "  + mt.wifi_status())
    print("- IP: "      + mt.get_ip_mac("ip"))
    print("- MAC: "     + mt.get_ip_mac("mac"))
        
    mt.set_ntp_server()
    #time.sleep(5)
    print("- NTP time: " + str(mt.set_datetime()))
    
    # TCP test

    srv="httpcan.org"
    #srv="httpbin.org"
    get="/get"

    #sts, _ = mt.atCMD("AT+CIPSSLCCONF=0")
    #sts, _ = mt.atCMD("AT+CIPSNIREQ=0")
    
    print("- Create TCP Connection")
    mt.create_conn(srv, 80, "TCP", keepalive=60)
    #mt.create_conn(srv, 443, "SSL", keepalive=60)

    print("- Send request")
    mt.send_data(f"GET {get} HTTP/1.1\r\nHost: {srv}\r\n\r\n")
    #mt.send_data_transparent(f"GET / HTTP/1.1\r\nHost: {srv}\r\n\r\n")
    
    print("- Receive data")
    sts, data = mt.rcvDATA(2048, True, 10)
    if sts:
        print(data)
    else:
        print("- No Data")
    
    #mt.close_conn() # if not closed by server
     
    #print("- Disconnecting ...")
    #mt.wifi_disconnect()

   