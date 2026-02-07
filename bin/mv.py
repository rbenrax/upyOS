import uos
import utls

def mv(sp, dp):

    sf = sp.split("/")[-1]
    if utls.isdir(dp):
        if not dp[-1]=="/": dp +="/"
        dp += sf
    
    print(sp + " -> " + dp)
    uos.rename(sp, dp)

def __main__(args):

    if len(args) != 2:
        print("Move a file or all files in directory\nUsage: mv <spath> <dpath>")
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
                mv(spath, dpath)
            else:
                if not spath[-1]=="/": spath +="/"
                
                if utls.isdir(dpath):
                    if not dpath[-1]=="/": dpath +="/"
                
                tmp=uos.listdir(spath)
                for f in tmp:
                    mv(spath+f, dpath)
                          
            
