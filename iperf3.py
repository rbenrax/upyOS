import iperf3

def __main__(args):

    if len(args) == 0:
        print("Find text in files\nUsage: grep <text> <options>: [-rv] (recursive, verbose) ")
        return
    
    mode=""
    ip=""
    
    if len(args) == 1:
       mode=args[0]
    elif len(args) > 1:
        mode=args[0]
        ip=args[1]

    if "s" in mode:
        server = iperf3.Server()
        result = server.run()
        print(result.remote_host)
        
    elif "c" in mode:
        client = iperf3.Client()
        client.duration = 1
        client.server_hostname = ip
        client.port = 5201
        result = client.run()
        print(result.sent_Mbps)

if __name__ == "__main__":

    args = ["-s"]
    __main__(args)
        
        

        
