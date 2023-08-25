import network
import sdata

#TODO: If conected, disconnect first
#      Prettify

def __main__(args):
    
    if not sdata.board["wifi"]:
        print ("wifi not available in this board")
        return
    
    if len(args) == 0:
        print ("WIFI management command\n Usage:")
        print ("wifi status - prints wifi client status")
        print ("wifi on - activate wifi client")
        print ("wifi off - deactivate wifi client")
        print ("wifi scan - list visible networks")
        print ("wifi connect <SSID> <PSK> - connect to network")
        print ("wifi ap - prints Access Point status")
        print ("wifi ap on - activate Access Point")
        print ("wifi ap off - deactivate Access Point")
        return

    sta_if = network.WLAN(network.STA_IF)
    cmd = args[0]
    
    if cmd == "on":
        sta_if.active(True)
    elif cmd == "off":
        sta_if.active(False)
    elif cmd == "status":
        print (f'WiFi is {"Active" if sta_if.active() == True else "Inactive"}')
        print (f"Status {sta_if.status()}")
        if sta_if.isconnected():
            print (f'WiFi connection is {"Established" if sta_if.isconnected() else "Not connected"}')
    elif cmd == "scan":
        for net in sta_if.scan():
            print ("SSID\tUnknown\tCHN\tSignal")
            print (f"{net[0]}\t{net[1]}\t{net[2]}\t{net[3]}\t")
    elif cmd == "connect":
        print (f"Connecting to {args[1]}")
        sta_if.connect(args[1], args[2])
        while not sta_if.isconnected():
            pass
        print ("Connected")
    elif cmd == "ap":
        ap_if = network.WLAN(network.AP_IF)
        cmd = args[1]
        if cmd == "on":
            ap_if.active(True)
        elif cmd == "off":
            ap_if.active(False)
        else:
            print ('Access point is {"Active" if ap_if.active() == True else "Inactive"}')

