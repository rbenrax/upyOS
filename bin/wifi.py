import network
from utime import sleep
from utls import tspaces
import sys

import sdata

def psts(nic, aif):

    print (f'wifi {nic}: {"Active" if aif.active() == True else "Not active"} ({aif.status()})')
    if nic=="sta":
        print (f"wifi {nic}: {'Connected' if aif.isconnected() else 'Not connected'}")
    else: # ap
        print (f"wifi {nic}: {'Client connected' if aif.isconnected() else 'No Client connected'}")

def __main__(args):
    
    if not sdata.board or not sdata.board["wifi"]:
        print("wifi not available in this board")
        return

    # Command: wifi sta config essid=RedQ password=xxx 
    #print(f"{args=}")

    if len(args) < 2:
        print("wifi management command\nUsage:")
        print("\t<nic>: sta/ap")
        print("\twifi <nic> status - prints wifi interfase status")
        print("\twifi <nic> on - activate wifi interfase")
        print("\twifi <nic> off - deactivate wifi interfase")
        print("\twifi <nic> scan - list visible wireless networks")
        print("\twifi <nic> config - show/set networks connection parameters (essid=<essid> password=<pass> ...")
        print("\twifi <nic> ifconfig - show/set: IPs parmeters (ip, mask, gateway, dns)")
        print("\twifi <nic> connect <SSID> <PSK> [Timeout] - connect to wireless network ap")
        print("\twifi <nic> disconnect - disconnect wifi comnection") 
        return

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
        psts(nic, _if)
            
    elif cmd == "scan":
        if nic=="ap":
            print("Only applicable to sta if")
            return

        if not _if.active():
            psts(nic, _if)
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
        
        if nic=="ap":
            print("Only applicable to sta if")
            return
   
        if not _if.active():
            psts(nic, _if)
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
            print("Disconnecting...")
            _if.disconnect()
            print("Disconnected")
                
    else:
        print(f"Invalid wifi commad {cmd}")

