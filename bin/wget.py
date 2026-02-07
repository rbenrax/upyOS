import urequests

def __main__(args):
    
    if len(args) == 0:
        print ("Get a file from the net\nUsage: wget <url>")
        return
    
    url = args[0]
    filename = ""
    if url.endswith("/"):
        filename = "index"
    else:
        filename = url.split("/")[-1].split("?")[0]
    
    r = urequests.get(url)
    try:
        with open(filename, "wb") as fp:
            while True:
                chunk = r.raw.read(512)
                if not chunk:
                    break
                fp.write(chunk)
    finally:
        r.close()
