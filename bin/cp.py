import uos
import utls

def __main__(args):

    if len(args) != 2:
        print("Copy file, cp <spath> <dpath>")
        return
    else:
        spath=args[0]
        dpath=args[1]
        
        if spath == "" or dpath=="": return
        if not utls.file_exists(spath):
            print("File source not exists.")
            return
        
        sfile = spath.split("/")[-1]
        try:
            uos.listdir(dpath)
            dpath += "/" + sfile
        except OSError:
            pass  
        
        if utls.protected(dpath):
            print("Can not overwrite system file!")
        else:                  
            with open(spath, 'rb') as fs:
                with open(dpath, "wb") as fd:
                    while True:
                        buf = fs.read(256)
                        if not buf:
                            break
                        fd.write(buf)



        
