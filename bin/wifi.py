import network
import sys
from utime import sleep
from utls import tspaces

import sdata

def __main__(args):
    
    if not sdata.board["wifi"]:
        print("wifi not available in this board")
        return
    
    if len(args) == 0:
        print("WIFI sta_if management command\nUsage:")
        print("wifi status - prints wifi client status")
        print("wifi on - activate wifi client")
        print("wifi off - deactivate wifi client")
        print("wifi scan - list visible networks")
        print("wifi config - show/set networks connect parms (essid=<essid> password=<pass> ...")
        print("wifi ifconfig - show/set: IPs parms (ip, mask, gateway, dns)")
        print("wifi connect <SSID> <PSK> [Tout] - connect to network")
        print("wifi disconnect - disconnect wifi client") 
        return

    sta_if = network.WLAN(network.STA_IF)
    cmd = args[0]
    
    if cmd == "on":
        if sta_if.isconnected():
            sta_if.disconnect()
            sta_if.active(False)
        sta_if.active(True)
        
    elif cmd == "off":
        sta_if.active(False)
        
    elif cmd == "status":
        print (f'WiFi is {"Active" if sta_if.active() == True else "Inactive"}')
        print (f"Status {sta_if.status()}")
        if sta_if.isconnected():
            print (f'WiFi connection is {"Established" if sta_if.isconnected() else "Not connected"}')
            
    elif cmd == "scan":
        from ubinascii import hexlify
        print ("SSID             \t  Bssid    \tCh   \tSig \tSec \tHid")
        for net in sta_if.scan():
            print (f"{tspaces(net[0].decode(), n=20, ab="a")}      {hexlify(net[1]).decode()}\t{net[2]}\t{net[3]}\t{net[4]}\t{net[5]}")
            
    elif cmd == "connect":
        """Conect <SSID> <pass> <Time out>"""
        
        if sta_if.isconnected(): return
            
        tout=0
        if len(args)==4:
            tout=int(args[3])
 
        print (f"Connecting to {args[1]}{', Time out in ' + str(tout) + 's.' if tout > 0 else ''}")

        sta_if.connect(args[1], args[2])
        
        while not sta_if.isconnected():
            if tout > 0:
                tout -= 1
                sleep(1)
                if tout < 1: break
            pass
        
        if sta_if.isconnected():
            print("Connected")
        else:
            print("Time out waiting connection")
    
    elif cmd == "config":
        """sta_if if.config(essid='micropython',password=b"micropython",channel=11,authmode=network.AUTH_WPA_WPA2_PSK)  #Set up an access point"""
        try:
            if len(args)==1:
                print("wifi_sta config - Show/Set: mac, [e]ssid, password, channel, hidden, security, key, reconects, txpower, pm, authmode")
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
                            print(mac2Str(sta_if.config(e)))
                        else:
                            print(sta_if.config(e))
                
                if len(p)>0:
                    #print(p)
                    sta_if.config(**p)
                    
        except Exception as ex:
            print("config err: " + str(ex) + ": " + str(e))
            if sdata.debug:
                sys.print_exception(ex)
            pass
        
    elif cmd == "ifconfig":
        try:
            if len(args)==1:
                ic = sta_if.ifconfig()
                from utls import mac2Str
                print (f"WiFi sta: inet {ic[0]} netmask {ic[1]} broadcast {ic[2]}")
                print (f"      MAC: {mac2Str(sta_if.config("mac"))}")
                print (f"      DNS: {ic[3]}")
                print (f"      status: {'Active' if sta_if.active() else 'Inactive'}")
                print (f"              {'Connected' if sta_if.isconnected() else 'Disconnected'}")
                
            elif len(args)==5:
                sta_if.ifconfig((args[1], args[2], args[3], args[4]))
                
        except Exception as ex:
            print("ifconfig err: " + str(ex))
            pass
        
    elif cmd == "disconnect":
        if sta_if.isconnected():
            print("Disconnecting...")
            sta_if.disconnect()
            print("Disconnected")
                

