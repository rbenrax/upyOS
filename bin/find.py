import sdata
import uos
import utls

def __main__(args):

    if len(args) == 0:
        print("Find files in directories\nUsage: find <pattern> [-r] [path]")
        return
    
    txt=args[0]
    mode=""
    path="/"
    
    if len(args) > 1:
        for a in args[1:]:
            if a == "-r":
                mode = "-r"
            else:
                path = a

    def search(atxt, apath, amode):
        try:
            tmp=uos.listdir(apath)
        except OSError:
            return
            
        tmp.sort()

        if apath != "/" and not apath.endswith("/"):
            apath+="/"
        
        for f in tmp:
            full_path = apath + f
            if atxt in f:
                print(f"Found: {full_path}")
            
            if utls.isdir(full_path) and "r" in amode:
                search(atxt, full_path, amode)

    search(txt, path, mode)

if __name__ == "__main__":
    args = ["re", "-r"]
    __main__(args)
        
        

        
