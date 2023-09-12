import urequests

def __main__(args):
    
    if len(args) == 0:
        print ("Get a file from the net\nUsage:wget <url>")
        return
    
    url = args[0]
    filename = ""
    if url.endswith("/"):
        filename = "index"
    else:
        filename = url.split("/")[-1].split("?")[0]
    fp = open(filename, "wt")
    r = urequests.get(url).raw
    while (True):
        read = r.read(100)
        fp.write(read)
        if len(read) < 100:
            break
    fp.close()
