import network
import sdata

def __main__(args):
    
    if not sdata.board["wifi"]:
        print ("wifi not available in this board")
        return
    
    w = network.WLAN(network.STA_IF)
    ic = w.ifconfig()
    print (f"WiFi sta: inet {ic[0]} netmask {ic[1]} broadcast {ic[2]}")
    print (f"      status: {'Active' if w.isconnected() else 'Inactive'}")
    print (f"      DNS {ic[3]}")