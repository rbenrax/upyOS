from uping import ping

def __main__(args):
    
    if len(args) == 1:
        mode=args[0]
    else:
        print ("Ping IP\nUsage: ping <ip>")
        return
    
    ping(args[0])
    
if __name__ == "__main__":
    a=["-h"]
    __main__(a)
        
