import network
from utime import sleep
from utls import tspaces
from utls import setenv
import sys

import sdata

# <network> Class, functions & constant 

#network.WLAN()
#network.PPP()      'ppp = network.PPP(modem.uart)'
#network.country()
#network.hostname()
#network.phy_mode

#network.STA_IF 0
#network.AP_IF 1

#network.AUTH_OPEN 0
#network.AUTH_WEP 1
#network.AUTH_WPA_PSK 2
#network.AUTH_WPA2_PSK 3
#network.AUTH_WPA_WPA2_PSK = 4
#network.AUTH_WPA2_ENTERPRISE 5
#network.AUTH_WPA3_PSK 6
#network.AUTH_WPA2_WPA3_PSK 7
#network.AUTH_WAPI_PSK 8
#network.AUTH_MAX 9
 
AUTHMODE = {0: "open", 1: "WEP", 2: "WPA-PSK", 3: "WPA2-PSK", \
            4: "WPA/WPA2-PSK", 5: "WPA2/ENTERPRISE",  6: "WPA3/PSK", \
            7: "WPA2/WPA3-PSK", 8: "WAPI-PSK", 9: "MAX"}
 
#network.MODE_11B 1
#network.MODE_11G 2
#network.MODE_11N 4
#network.MODE_LR 8

NETMODE = {1: "11B", 2: "11G", 4: "11N", 8: "LR"}

#network.STAT_ASSOC_FAIL 203
#network.STAT_BEACON_TIMEOUT 200
#network.STAT_CONNECTING 1001
#network.STAT_GOT_IP 1010
#network.STAT_HANDSHAKE_TIMEOUT 204
#network.STAT_IDLE 1000
#network.STAT_NO_AP_FOUND 201
#network.STAT_WRONG_PASSWORD 202

NETSTAT = {203: "Association fail", 200: "Beacon timeout", 1001: "Connecting", 1010: "Got IP", \
           204: "Handshake timeout", 1000: "Idle", 201: "No AP found",  202: "Wrong password"}

def psts(mods, nic, aif):

    if not "-n" in mods:
        if nic=="sta":
            print (f'wifi {nic}: {"Active" if aif.active() == True else "Not active"} ({NETSTAT[aif.status()]})')
            print (f"wifi {nic}: {'Connected' if aif.isconnected() else 'Not connected'}")
        else: # ap
            print (f'wifi {nic}: {"Active" if aif.active() == True else "Not active"}')
            print (f"wifi {nic}: {'Client connected' if aif.isconnected() else 'No Client connected'}")
        
    if aif.active():
        setenv("0", "1")
    else:
        setenv("0", "0")
        
    if aif.isconnected():
        setenv("1", "1")
    else:
        setenv("1", "0")
        
def __main__(args):
    
    if not sdata.board or not sdata.board["wifi"]:
        print("wifi not available in this board")
        return

    # Command: wifi sta config essid=RedQ password=xxx 
    #print(f"{args=}")

    if len(args) == 0:
        print("wifi management command\nUsage:")
        print("\twifi sta/ap status - show wifi interfase status")
        print("\twifi sta/ap on - activate wifi interfase")
        print("\twifi sta/ap off - deactivate wifi interfase")
        print("\twifi sta scan - list visible wireless networks")
        print("\twifi sta/ap config - show/set networks connection parameters (essid=<essid> password=<pass> ...")
        print("\twifi sta/ap ifconfig - show/set: IPs parmeters (ip, mask, gateway, dns)")
        print("\twifi sta connect <SSID> <PSK> [Timeout] - connect to wireless network ap")
        print("\twifi sta disconnect - disconnect wifi comnection")
        print("\twifi country <country> - get/set country")
        print("\twifi hostname <hostname> - get/set hostname")
        print("\twifi phy_mode <phy_mode> - get/set phy_mode")
        print("\twifi --info parm info")
        return

    mods=[]

    for a in args:      # adds modifiers
        if a[0] == "-":
            mods.append(a)
            
    if "--info" in mods:
        with open("/bin/wifi.inf", 'r') as f:
            while True:
                lin = f.readline()
                if not lin: break
                print(lin, end="")
        return
    
    if args[0] == "country":
        if len(args) == 2:
            network.country(args[1])
        else:
            print(network.country())
        return
    
    if args[0] == "hostname":
        if len(args) == 2:
            network.hostname(args[1])
        else:
            print(network.hostname())
        return
    
    if args[0] == "phy_mode":
        if len(args) == 2:
            network.phy_mode(args[1])
        else:
            print(network.phy_mode())
        return
    
#- - - - -

    nic = args[0]
    if nic not in ["sta", "ap"]:
        print("wifi, <nic> shoud be sta or ap")
        return

    _if=None
    if nic=="sta":
        _if = network.WLAN(network.STA_IF)
    else:
        _if = network.WLAN(network.AP_IF)
        
    cmd = args[1]
    
    if cmd == "on":
        _if.active(False)
        _if.active(True)
        
    elif cmd == "off":
        _if.active(False)
        
    elif cmd == "status":
        psts(mods, nic, _if)
            
    elif cmd == "scan":
        if nic=="ap":
            print("Only applicable to sta if")
            return

        if not _if.active():
            psts(mods, nic, _if)
            return

        try:
            from utls import mac2Str
            print ("SSID             \t  Bssid    \t\tCh   \tSig \tSec \t\tHid")
    
            for net in _if.scan():
                print (f"{tspaces(net[0].decode(), n=20, ab="a")}      {mac2Str(net[1])}\t{net[2]}\t{net[3]}\t{net[4]}-{AUTHMODE[net[4]]}\t{net[5]}")

        except Exception as ex:
            print("wifi err: " + str(ex))
            sys.print_exception(ex)
            pass
            
    elif cmd == "connect":
        """Conect <SSID> <pass> <Time out>"""
        
        if nic=="ap":
            print("Only applicable to sta if")
            return
   
        if not _if.active():
            psts(mods, nic, _if)
            return
    
        if _if.isconnected():
            print(f"{nic} already connected")
            return
            
        tout=0
        if len(args)==5:
            tout=int(args[4])
 
        print (f"Connecting to {args[2]}{', Time out in ' + str(tout) + 's.' if tout > 0 else ''}")

        try:
            _if.connect(args[2], args[3])
            
            while not _if.isconnected():
                if tout > 0:
                    tout -= 1
                    sleep(1)
                    if tout < 1: break
                pass
            
            if _if.isconnected():
                print("Connected")
            else:
                print("Time out waiting connection")
                _if.active(False)
                _if.active(True)
                
        except Exception as ex:
            print("wifi err: " + str(ex))
            if sdata.debug:
                sys.print_exception(ex)
            pass
    
    elif cmd == "config":
        """sta_if if.config(essid='micropython',password=b"micropython",channel=11,authmode=network.AUTH_WPA_WPA2_PSK)  #Set up an access point"""
        try:
            if len(args)==2:
                print("wifi_sta config - Show/Set: mac, [e]ssid, password, channel, hidden, security, key, reconects, txpower, pm, authmode")
                return
            
            if len(args)>2:
                p={}
                for e in args[2:]:
                    if "=" in e:
                        tmp=e.split("=")
                        # TODO: check type
                        if tmp[0]in ["mac", "channel", "authmode", "key", "security"]: tmp[1]=int(tmp[1])
                        p[tmp[0]]=tmp[1]

                    else:
                        if e == "mac":
                            from utls import mac2Str
                            print(mac2Str(_if.config(e)))
                        else:
                            print(_if.config(e))
                
                if len(p)>0:
                    #print(p)
                    _if.config(**p)
                    
        except Exception as ex:
            print("wifi err: " + str(ex) + ": " + str(e))
            if sdata.debug:
                sys.print_exception(ex)
            pass
        
    elif cmd == "ifconfig":
        try:
            if len(args)==2:
                ic = _if.ifconfig()
                from utls import mac2Str
                print (f"wifi {nic}: inet {ic[0]} netmask {ic[1]} broadcast {ic[2]}")
                print (f"     MAC: {mac2Str(_if.config("mac"))}")
                print (f"     DNS: {ic[3]}")
                print (f"  Status: {'Active' if _if.active() else 'Not active'}")
                if nic=="sta":
                    print (f"          {'Connected' if _if.isconnected() else 'Not connected'}")
                else:
                    print (f"          {'Clients connected' if _if.isconnected() else 'No Client connected'}")
                
            elif len(args)==6:
                _if.ifconfig((args[2], args[3], args[4], args[5]))
                #_if.ifconfig(('192.168.3.4', '255.255.255.0', '192.168.3.1', '8.8.8.8'))
            else:
                print("Error, valid IPs parameters: wifi ifconfig <nic> <ip> <mask> <gw> <dns>")
                
        except Exception as ex:
            print("wifi err: " + str(ex))
            pass
        
    elif cmd == "disconnect":
        if nic=="ap":
            print("Only applicable to sta if")
            return
        
        if _if.isconnected():
            if not "-n" in mods:
                print("Disconnecting...")
            _if.disconnect()
            if not "-n" in mods:
                print("Disconnected")
                
    else:
        print(f"Invalid wifi commad {cmd}")

