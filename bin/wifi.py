import network
import sdata
from utime import sleep
from utls import tspaces

#TODO: If conected, disconnect first
#      Prettify

def __main__(args):
    
    if not sdata.board["wifi"]:
        print ("wifi not available in this board")
        return
    
    if len(args) == 0:
        print ("WIFI sta_if management command\n Usage:")
        print ("wifi status - prints wifi client status")
        print ("wifi on - activate wifi client")
        print ("wifi off - deactivate wifi client")
        print ("wifi scan - list visible networks")
        print ("wifi config - list/set networks connect parms")
        print ("wifi ifconfig - list/set networks ip parms")
        print ("wifi connect <SSID> <PSK> [Tout] - connect to network")
        print ("wifi disconnect - disconnect wifi client") 
        print ("wifi ap - prints Access Point status")
        print ("wifi ap on - activate Access Point")
        print ("wifi ap off - deactivate Access Point")
        return

    sta_if = network.WLAN(network.STA_IF)
    cmd = args[0]
    
    if cmd == "on":
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
        print ("SSID  \t\tBssid    \tCh   \tSig \tSec \tVis")
        for net in sta_if.scan():
            print (f"{tspaces(net[0].decode(), n=12, ab="a")} \t{hexlify(net[1]).decode()}\t{net[2]}\t{net[3]}\t{net[4]}\t{net[5]}")
            
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
        try:
            if len(args)==2:
                print(sta_if.config(args[1]))
            elif len(args)==3:
                sta_if.config(args[1] + "=" + args[2])
        except Exception as ex:
            print("config err: " + str(ex))
            pass
        
    elif cmd == "ifconfig":
        try:
            if len(args)==1:
                #w = network.WLAN(network.STA_IF)
                ic = sta_if.ifconfig()
                print (f"WiFi sta: inet {ic[0]} netmask {ic[1]} broadcast {ic[2]}")
                print (f"      status: {'Active' if sta_if.isconnected() else 'Inactive'}")
                print (f"      DNS {ic[3]}")
                
            elif len(args)==5:
                sta_if.ifconfig(args[1], args[2], args[3], args[4])
        except Exception as ex:
            print("ifconfig err: " + str(ex))
            pass
        
    elif cmd == "disconnect":
        if sta_if.isconnected():
            print("Disconnecting...")
            sta_if.disconnect()
            print("Disconnected")
                
    elif cmd == "ap":
        ap_if = network.WLAN(network.AP_IF)
        cmd = args[1]
        if cmd == "on":
            ap_if.active(True)
        elif cmd == "off":
            ap_if.active(False)
        else:
            print ('Access point is {"Active" if ap_if.active() == True else "Inactive"}')

