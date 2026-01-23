import sdata
import uos
import utls

def __main__(args):

    if len(args) == 0:
        print("Find files in directories\nUsage: find <option>: <pattern> [-r]")
        return
    
    txt=""
    mode=""
    
    if len(args) == 1:
       txt=args[0]
    elif len(args) > 1:
        txt=args[0]
        mode=args[1]

    def search(atxt, apath, amode):
        tmp=uos.listdir(apath)
        tmp.sort()
        #print(f"{atxt=} {apath=} {amode=}")

        if apath !="/" and len(apath)>1:
            apath+="/"
        
        for f in tmp:
            if not utls.isdir(f):
                if atxt in f:
                    print(f"Found: {apath}{f}")
                        
            elif "r" in mode:
                search(atxt, apath + f, amode)

    search(txt, "", mode)

if __name__ == "__main__":

    args = ["re", "-r"]
    __main__(args)
        
        

        
