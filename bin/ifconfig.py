import network
import sdata

def __main__(args):
    w = network.WLAN(network.STA_IF)
    ic = w.ifconfig()
    print ("WiFi: inet {} netmask {} broadcast {}".format(ic[0], ic[1], ic[2]))
    print ("      status: {}".format("Active" if w.isconnected() else "Inactive"))
    print ("      DNS {}".format(ic[3]))