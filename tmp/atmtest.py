
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
    mt.scmds = True
    mt.sresp = True
    mt.timing = True
    
    def get(url, filename=""):
        prot, _, hostport, path = url.split('/', 3)
        port = 443 if prot.lower() == "https:" else 80
        con = "SSL" if prot.lower() == "https:" else "TCP"

        tmp = hostport.split(':')
        if len(tmp) == 1:
            host = tmp[0]
        else:
            host = tmp[0]
            port = tmp[1]

        mt.create_conn(host, port, con, keepalive=60)
        
        mt.atCMD("ATE0")
        mt.atCMD("AT+CIPMODE=1")
        
        if not path.startswith("/"): path = "/" + path
        
        req = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\nUser-Agent: upyOS\r\nAccept: */*\r\n\r\n"
        #req = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nUser-Agent: upyOS\r\nAccept: */*\r\n\r\n"

        # Entrar en modo transparente
        mt.send_passthrow()
        
        time.sleep_ms(30)
        mt._drain()
        time.sleep_ms(30)
        mt.modem.write(req.encode('utf-8'))
        time.sleep_ms(30)
        sts = False
        with open(filename, 'wb') as f:
            sts, headers = mt.rcv_to_file_t(f, 8)
        
        time.sleep_ms(600)
        mt.modem.write("+++")
        time.sleep_ms(600)
        mt.atCMD("AT+CIPMODE=0", 3)
        mt.close_conn()
        mt.atCMD("ATE1", 2)
    

    testb = f'https://raw.githubusercontent.com/rbenrax/upyOS/refs/heads/test/libx/microWebSrv.py'
    get(testb, filename="/x1.py")

    testb = f'https://raw.githubusercontent.com/rbenrax/upyOS/refs/heads/test/libx/uftpdserver.py'
    get(testb, filename="/x2.py")

    testb = f'https://raw.githubusercontent.com/rbenrax/upyOS/refs/heads/test/libx/editor.py'
    get(testb, filename="/x3.py")
 

    if 1 == 2:

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
        #srv="192.168.2.132"
        #srv="fmstream.org"
        #get="/"

        srv= "raw.githubusercontent.com"
        #get= "/rbenrax/upyOS/refs/heads/main/etc/upgrade2.inf"
        get= "/rbenrax/upyOS/refs/heads/main/libx/microWebSrv.py"    
    

        #print("Ping: " + mt.ping(srv))
        
        print("- Create TCP Connection")
        #mt.create_conn(srv, 8200, "TCP", keepalive=60)
        mt.create_conn(srv, 443, "SSL", keepalive=60)
        
        mt.atCMD("ATE0")
        mt.atCMD("AT+CIPMODE=1")
        
        print("- Send request")
        #req = f"GET {get} HTTP/1.1\r\nHost: {srv}\r\nConnection: close\r\nUser-Agent: upyOS\r\nAccept: */*\r\n\r\n"
        req = f"GET {get} HTTP/1.1\r\nHost: {srv}\r\nUser-Agent: upyOS\r\nAccept: */*\r\n\r\n"

        # Entrar en modo transparente
        #mt.modem.write("AT+CIPSEND\r\n")
        mt.send_passthrow()
        
        time.sleep(.5)
        print(f"Sending: {req}")
        mt.modem.write(req)
        while mt.modem.any():
            mt.modem.read()
        time.sleep(.3)

        #sts, ret = mt.send_data(req)
        #sts, ret = mt.send_data_transp(req, 5)
        #print(f"- sts: {sts} / ret: {ret}")
        
        f = open('datos.txt', 'w')
        
        print("- Data receiving")
        #sts, data = mt.rcv_data(0, True, 10, f)
        
        #sts, body, headers = mt.rcv_data(0, True, 15)
        #if sts:
        #    print(body)
        #    f.write(body)
        #else:
        #    print("- No Data")
        
        sts, headers = mt.rcv_to_file_t(f, 10)
        if sts:
            print(headers)
        else:
            print("- No Data")

        f.close()
        
        mt.modem.write("+++")
        mt.atCMD("AT+CIPMODE=0")
        mt.close_conn() # if not closed by server
        mt.atCMD("ATE1")
        
        #print("- Disconnecting ...")
        #mt.wifi_disconnect()

       
       
         
        """  
        ATE0
        AT+RST

        AT+CWJAP="MiSSID","MiPassword"
        AT+CIPSTA?

        AT+CIPSTART="SSL","example.com",443
        AT+CIPMODE=1
        AT+CIPSEND
        GET / HTTP/1.1
        Host: example.com
        Connection: close

        +++
        AT+CIPMODE=0
        AT+CIPCLOSE
        """   
