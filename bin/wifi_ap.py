import network
import sys

import sdata

def __main__(args):
    
    if not sdata.board["wifi"]:
        print ("wifi not available in this board")
        return
    
    if len(args) == 0:
        print("WIFI AP management command\nUsage:")
        print("wifi status - prints wifi AP status")
        print("wifi on - activate wifi AP")
        print("wifi off - deactivate wifi AP")
        print("wifi config - show/set networks connect parms (essid=<essid> password=<pass> ...")
        print("wifi ifconfig - show/set: IPs parms (ip, mask, gateway, dns)")
        return

    ap_if = network.WLAN(network.AP_IF)
    cmd = args[0]
    
    if cmd == "on":
        if ap_if.active():
            ap_if.active(False)
        ap_if.active(True)
        
    elif cmd == "off":
        ap_if.active(False)
        
    elif cmd == "status":
        print (f'WiFi ap_if is {"Active" if ap_if.active() == True else "Inactive"}')
    
    elif cmd == "config":
        """ap_if.config(essid='micropython',password=b"micropython",channel=11,authmode=network.AUTH_WPA_WPA2_PSK)  #Set up an access point"""
        try:
            if len(args)==1:
                print("wifi_ap config - Show/Set: mac, [e]ssid, password, channel, hidden, security, key, reconects, txpower, pm, authmode")
                return
            
            if len(args)>1:
                #print(args[1])
                p={}
                for e in args[1:]:
                    if "=" in e:
                        tmp=e.split("=")
                        # TODO: check type
                        if tmp[0]in ["mac", "channel", "authmode", "key"]: tmp[1]=int(tmp[1])
                        p[tmp[0]]=tmp[1]

                    else:
                        if e == "mac":
                            from utls import mac2Str
                            print(mac2Str(ap_if.config(e)))
                        else:
                            print(ap_if.config(e))
                
                if len(p)>0:
                    #print(p)
                    ap_if.config(**p)
                    
        except Exception as ex:
            print("config err: " + str(ex) + ": " + str(e))
            if sdata.debug:
                sys.print_exception(ex)
            pass
        
    elif cmd == "ifconfig":
        """config=('192.168.178.107', '255.255.255.0', '192.168.178.1', '8.8.8.8')"""
        try:
            if len(args)==1:
                ic = ap_if.ifconfig()
                print (f"WiFi ap: inet {ic[0]} netmask {ic[1]} broadcast {ic[2]}")
                print (f"      status: {'Active' if ap_if.isconnected() else 'Inactive'}")
                print (f"      DNS {ic[3]}")
                
            elif len(args)==5:
                ap_if.ifconfig((args[1], args[2], args[3], args[4]))
                
        except Exception as ex:
            print("ifconfig err: " + str(ex))
            if sdata.debug:
                sys.print_exception(ex)

            pass
