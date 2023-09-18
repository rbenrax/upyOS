import network
import sdata

def __main__(args):
    
    if not sdata.board["wifi"]:
        print ("wifi not available in this board")
        return
    
    def pif(i, nif):
        ic = nif.ifconfig()
        from utls import mac2Str
        print (f"WiFi {i}: inet {ic[0]} netmask {ic[1]} broadcast {ic[2]}")
        print (f"      MAC: {mac2Str(nif.config("mac"))}")
        print (f"      DNS: {ic[3]}")
        print (f"      status: {'Active' if nif.active() else 'Inactive'}")
        print (f"              {'Connected' if i == "sta" and nif.isconnected() else 'Disconnected'}")
    
    sta_if = network.WLAN(network.STA_IF)
    pif("sta", sta_if)
    
    ap_if = network.WLAN(network.AP_IF)
    pif("ap", ap_if)