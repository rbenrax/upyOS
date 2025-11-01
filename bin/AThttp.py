
# MQTT manager

from ATmodem import ModemManager
import time
import sdata
import utls
import sys

proc=None

class HttpManager(ModemManager):
    
    def __init__(self, device="modem0"):
        super().__init__(device)

        self.debug = False
        self.buffer = "" # Message buffer
        
    # MQTT CMDs

    def mqtt_sub(self, topic="", qos=0):
        #AT+HTTPCLIENT=<opt>,<content-type>,<"url">,[<"host">],[<"path">],<transport_type>[,<"data">][,<"http_req_header">][,<"http_req_header">][...]
        cmd = f''
        sts, resp = self.atCMD(cmd, 1)
        return sts
    
    def mqtt_list_subs(self):
        sts, res = self.atCMD(f'AT+MQTTSUB?', 1)
        sl=""
        if sts:
            for l in res.split():
                if l.startswith("+MQTTSUB:0"):           
                    sl += l.split(",")[2] + "\n"
        return sl


# ---------
    

    

    

# ---------

def __main__(args):

    #TODO: add qos, reconnect and others parms

    if len(args) == 0 or "--h" in args:
        print("HTTP Library and command line utility for AT-ESP serial modem")
        print("Usage:\t ")
        print("\t ATmqtt <pub> -t <topic> -m <message> [-q <qos> -r <retain>]")
        return

    def parse(mod):
        try:
            if mod in args:
                i = args.index(mod)
                if i+1 < len(args):
                    return args[i + 1] if i > 0 else ""
                else:
                    print(mod + " value, not found")
                    return ""
            else:
                return ""
        except Exception as ex:
            print("ATmqtt modifier error, " + mod)
            if sdata.debug:
                sys.print_exception(ex)
            return ""

    cmd = args[0]

    host  = parse("-h")
    port  = parse("-p")
    port  = int(port) if port != "" else 1883

    mm = HttpManager() # default dev= sdata.modem0
    
    # If modem not connected
    if not mm.modem:
        print("No connected")
        return
    
    if "-v" in args:
        mm.sctrl = True
        mm.scmds = True
        mm.sresp = True
        args = [arg for arg in args if arg != "-v"]
        
    if "-tm" in args:
        mm.timming = True
        args = [arg for arg in args if arg != "-tm"]
    
    # WIFI Connection by ESP-AT
    #mm.resetHW(22, 2)
    #if not mm.createUART(1, 115200, 4, 5):
    #    return
    
    #mm.set_moide(1)
    #mm.wifi_connect("SSID","PASSW")
    
    #print("Test: "     + str(mm.test_modem()))
    #print("Version: "  + mm.get_version())
    #print("Local IP: " + mm.get_ip_mac("ip"))
    #print("MAC: "      + mm.get_ip_mac("mac"))

    #print(mm.set_ntp_server())
    #time.sleep(5)
    #print(mm.set_datetime())

    connected = utls.getenv("mqtt")
    
    if connected != "c":
        
        if not "-h" in args:
            print("-h required")
            return

        mm.mqtt_user(1, sdata.sid, user, passw)
        if mm.mqtt_connect(host, port, recon):
            utls.setenv("mqtt", "c")
        else:
            utls.setenv("mqtt", "")
            print("No connected")
            return

    if cmd == "pub":
        if not "-t" in args or topic == "":
            print("-t required")
            return
        if not "-m" in args or messg == "":
            print("-m required")
            return
        if mm.mqtt_pub(topic, messg, qos, retain):
            print(f"Message '{topic}': '{messg}' published")
        else:
            print(f"Publish '{topic}': '{messg}' failed")
        
    elif cmd == "sub":
        if not "-t" in args or topic == "":
            print("-t required")
            return
        if mm.mqtt_sub(topic, qos):
            print(f"Subscription '{topic}' Ok")
        else:
            print(f"Subscription '{topic}' failed")
    else:
       print(f"HTTP not valid subcommand {cmd}")

    if cmd "-l" in args:
        print("Listening MQTT messages...")
        while True:
            
            # Thread control
            if proc.sts=="S":break

            if proc.sts=="H":
                time.sleep(1)
                continue
            
            messages = mm.check_messages()
            if messages:
                for msg in messages:
                    print(f"{msg['topic']}: {msg['data']}")
            time.sleep(0.1)