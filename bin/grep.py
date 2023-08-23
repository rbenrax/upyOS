import sdata
import uos
import utls

def __main__(args):

    if len(args) == 0:
        print("Find text in files, grep <option>: <text> [-r] ")
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
                with open(apath + f, "r") as fh:
                    ft=fh.read()
                    if ft.find(atxt)!=-1:
                        print(f"Found: {apath}{f}")
                        
            elif "r" in mode:
                search(atxt, f, amode)

    search(txt, "", mode)

if __name__ == "__main__":

    args = ["sys", "-r"]
    __main__(args)
        
        

        
