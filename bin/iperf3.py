import uiperf3

def __main__(args):

    if len(args) == 0:
        print("Test network performance\nUsage: iperf3 -s / iperf3 -c <destIP>")
        return
    
    mode=""
    ip=""
    
    if len(args) == 1:
       mode=args[0]
    elif len(args) > 1:
        mode=args[0]
        ip=args[1]

    if mode == "-s":
        uiperf3.server()    
    elif mode == "-c":
        uiperf3.client(ip, udp=True, reverse=True)

