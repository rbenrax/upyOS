import uos
import utls

def __main__(args):

    if len(args) != 2:
        print("Move file, mv <spath> <dpath>")
        return
    else:
        spath=args[0]
        dpath=args[1]
        
    if spath == "" or dpath == "": return
    
    if not utls.file_exists(spath):
        print("File source not exists.")
        return

    sfile = spath.split("/")[-1]
    try:
        uos.listdir(dpath)
        dpath += "/" + sfile
    except OSError:
        pass

    if utls.protected(spath):
        print("Can not move system files!")
    else:
        uos.rename(spath, dpath)

#if __name__ == "__main__":

#    args = ["/main.py", "/tmp"]
#    __main__(args)
        
        

        
