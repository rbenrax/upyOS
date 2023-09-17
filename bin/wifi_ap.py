import network
import sdata
from utime import sleep
from utls import tspaces
import sys

#TODO: If conected, disconnect first
#      Prettify

def __main__(args):
    
    if not sdata.board["wifi"]:
        print ("wifi not available in this board")
        return
    
    if len(args) == 0:
        print ("WIFI ap_if management command\n Usage:")
        print ("wifi status - prints wifi AP status")
        print ("wifi on - activate wifi AP")
        print ("wifi off - deactivate wifi AP")
        print ("wifi config - list/set networks connect parms")
        print ("wifi ifconfig - list/set networks ip parms")
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
        """ap.config(essid='micropython',password=b"micropython",channel=11,authmode=network.AUTH_WPA_WPA2_PSK)  #Set up an access point"""
        try:
            if len(args)==1:
                print("wifi_ap config - Show/Set: mac, ssid, channel, hidden, security, key, hostname, reconects, txpower, pm")
                return
            if len(args)==2:
                print(args[1])
                if "=" in args[1]:
                    ap_if.config(args[1])
                else:
                    print(ap_if.config(args[1]))
        except Exception as ex:
            print("config err: " + str(ex))
            if sdata.debug:
                sys.print_exception(ex)
            pass
        
    elif cmd == "ifconfig":
        """config=('192.168.178.107', '255.255.255.0', '192.168.178.1', '8.8.8.8')"""
        try:
            if len(args)==1:
                print("wifi_ap ifconfig - Show/Set: (ip, mask, gateway, dns)")
                return
            if len(args)==1:
                #w = network.WLAN(network.ap_if)
                ic = ap_if.ifconfig()
                print (f"WiFi sta: inet {ic[0]} netmask {ic[1]} broadcast {ic[2]}")
                print (f"      status: {'Active' if ap_if.isconnected() else 'Inactive'}")
                print (f"      DNS {ic[3]}")
                
            elif len(args)==5:
                ap_if.ifconfig(args[1], args[2], args[3], args[4])
        except Exception as ex:
            print("ifconfig err: " + str(ex))
            if sdata.debug:
                sys.print_exception(ex)

            pass
