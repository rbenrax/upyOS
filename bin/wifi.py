import network
import sys
from utime import sleep
from utls import tspaces

import sdata

def psts(nif, aif):
    print (f'wifi {nif} is {"Active" if aif.active() == True else "Inactive"}')

def __main__(args):
    
    if not sdata.board or not sdata.board["wifi"]:
        print("wifi not available in this board")
        return

    # Command: wifi sta config essid=RedQ password=xxx 

    if len(args) < 2:
        print("wifi management command\nUsage:")
        print("\t<nif>: sta/ap")
        print("\twifi <nif> status - prints wifi client status")
        print("\twifi <nif> on - activate wifi client")
        print("\twifi <nif> off - deactivate wifi client")
        print("\twifi <nif> scan - list visible networks")
        print("\twifi <nif> config - show/set networks connect parms (essid=<essid> password=<pass> ...")
        print("\twifi <nif> ifconfig - show/set: IPs parms (ip, mask, gateway, dns)")
        print("\twifi <nif> connect <SSID> <PSK> [Tout] - connect to network")
        print("\twifi <nif> disconnect - disconnect wifi client") 
        return

    if args[0] not in ["sta", "ap"]:
        print("wifi, <nif> shoud be sta or ap")
        return

    _if=None
    if args[0]=="sta":
        _if = network.WLAN(network.STA_IF)
    else:
        _if = network.WLAN(network.AP_IF)
        
    cmd = args[1]
    
    #print(f"{args=}")
    
    if cmd == "on":
        _if.active(False)
        _if.active(True)
        
    elif cmd == "off":
        _if.active(False)
        
    elif cmd == "status":
        psts(args[0], _if)
        #print (f"Status {_if.status()}")
        if args[0]=="sta" and _if.isconnected():
            print (f'wifi connection is {"Established" if _if.isconnected() else "Not connected"}')
            
    elif cmd == "scan":
        if args[0]=="ap":
            print("Only applicable to sta if")
            return

        if not _if.active():
            psts(args[0], _if)
            return

        try:
            from ubinascii import hexlify
            print ("SSID             \t  Bssid    \tCh   \tSig \tSec \tHid")

            for net in _if.scan():
                print (f"{tspaces(net[0].decode(), n=20, ab="a")}      {hexlify(net[1]).decode()}\t{net[2]}\t{net[3]}\t{net[4]}\t{net[5]}")

        except Exception as ex:
            print("wifi err: " + str(ex))
            pass
            
    elif cmd == "connect":
        """Conect <SSID> <pass> <Time out>"""
        
        if args[0]=="ap":
            print("Only applicable to sta if")
            return
   
        if not _if.active():
            psts(args[0], _if)
            return
    
        if _if.isconnected():
            print(f"{args[0]} already connected")
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
                        if tmp[0]in ["mac", "channel", "authmode", "key"]: tmp[1]=int(tmp[1])
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
                print (f"wifi {args[0]}: inet {ic[0]} netmask {ic[1]} broadcast {ic[2]}")
                print (f"     MAC: {mac2Str(_if.config("mac"))}")
                print (f"     DNS: {ic[3]}")
                print (f"  Status: {'Active' if _if.active() else 'Inactive'}")
                if args[0]=="sta":
                    print (f"          {'Connected' if _if.isconnected() else 'Disconnected'}")
                
            elif len(args)==6:
                _if.ifconfig((args[2], args[3], args[4], args[5]))
                #_if.ifconfig(('192.168.3.4', '255.255.255.0', '192.168.3.1', '8.8.8.8'))
            else:
                print("Error, valid IPs parameters: wifi ifconfig <nif> <ip> <mask> <gw> <dns>")
                
        except Exception as ex:
            print("wifi err: " + str(ex))
            pass
        
    elif cmd == "disconnect":
        if args[0]=="ap":
            print("Only applicable to sta if")
            return
        
        if _if.isconnected():
            print("Disconnecting...")
            _if.disconnect()
            print("Disconnected")
                
    else:
        print(f"Invalid wifi commad {cmd}")

