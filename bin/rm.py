import uos
import utls

def __main__(args):

    if len(args) != 1:
        print("Remove file\nUsage: rv <path>")
        return
    else:
        path=args[0]
        if path == "": return
        if utls.protected(path):
            print("Can not remove system file")
        else:
            uos.remove(path)
        
        

        
