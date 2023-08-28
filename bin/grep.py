import uos
import utls

def __main__(args):

    if len(args) == 0:
        print("Find text in files\nUsage: grep <text> <options>: [-rv] (recursive, verbose) ")
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
            if apath[-1] != "/": apath+="/"
        
        for f in tmp:
            if not utls.isdir(apath + f):
                #print(f"{apath + f}")
                with open(apath + f, "r") as fh:
                    while True:
                        ft=fh.readline()
                        if not ft: break

                        if ft.find(atxt)>-1:
                            print(f"Found: {apath}{f}")
                            if "v" in mode:
                                print(f"{ft}")

            elif "r" in mode:
                search(atxt, apath + f, amode)

    search(txt, "", mode)

if __name__ == "__main__":

    args = [".read(", "-rv"]
    __main__(args)
        
        

        
