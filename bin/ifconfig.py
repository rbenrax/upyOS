import network
import sdata

def __main__(args):
    
    if not sdata.board["wifi"]:
        print ("wifi not available in this board")
        return
    
    def pif(nic, nif):
        _if = nif.ifconfig()
        from utls import mac2Str
        print (f"WiFi {nic}: inet {_if[0]} netmask {_if[1]} broadcast {_if[2]}")
        print (f"     MAC: {mac2Str(nif.config("mac"))}")
        print (f"     DNS: {_if[3]}")
        print (f"  Status: {'Active' if nif.active() else 'Inactive'}")
        if nic=="sta":
            print (f"          {'Connected' if nif.isconnected() else 'Disconnected'}")
        else:
            print (f"          {'Clients connected' if nif.isconnected() else 'No Client connected'}")
        print("")

    # TODO: enumerate nic
    pif("sta", network.WLAN(network.STA_IF))
    pif("ap", network.WLAN(network.AP_IF))