import uos
import utls

def cp(sp, dp):

    sf = sp.split("/")[-1]
    if utls.isdir(dp):
        if not dp[-1]=="/": dp +="/"
        dp += sf
    
    print(sp + " -> " + dp)
    with open(sp, 'rb') as fs:
        with open(dp, "wb") as fd:
            while True:
                buf = fs.read(256)
                if not buf:
                    break
                fd.write(buf)


def __main__(args):

    if len(args) != 2:
        print("Copy file\nUsage: cp <spath> <dpath>")
        return
    else:
        spath=args[0]
        dpath=args[1]
        
        if spath == "" or dpath=="": return
        
        if not utls.file_exists(spath):
            print("File source not exists.")
            return
        
        if utls.protected(dpath):
            print("Can not overwrite system file!")
        else:
            if not utls.isdir(spath):
                cp(spath, dpath)
            else:
                if utls.isdir(spath):
                    if not spath[-1]=="/": spath +="/"
                    
                    if utls.isdir(dpath):
                        if not dpath[-1]=="/": dpath +="/"
                    
                    tmp=uos.listdir(spath)
                    for f in tmp: 
                        cp(spath+f, dpath)
                else:
                    print("not a valid paths " + spath)
                          
            



        
