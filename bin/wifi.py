import network

def __main__(args):
    print(args)
    if len(args) == 0:
        print ("Usage:")
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
        print ("WiFi is {}".format("Active" if sta_if.active() == True else "Inactive"))
        print ("Status {}".format(sta_if.status()))
        if sta_if.isconnected():
            print ("WiFi connection is {}".format("Established" if sta_if.isconnected() else "Not connected"))
    elif cmd == "scan":
        for net in sta_if.scan():
            print ("SSID\tUnknown\tCHN\tSignal")
            print ("{}\t{}\t{}\t{}\t".format(net[0], net[1], net[2], net[3]))
    elif cmd == "connect":
        print ("Connecting to {}".format(args[3]))
        sta_if.connect(args[3], args[4])
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
            print ("Access point is {}".format("Active" if ap_if.active() == True else "Inactive"))

