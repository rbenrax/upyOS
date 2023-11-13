import uos
import utls

def __main__(args):

    if len(args) == 0 or args[0]="--h":
        print("Remove file\nUsage: rm <path>")
        return
    else:
        for path in args:
            if utls.protected(path):
                print(f"Can not remove system file {path}")
            else:
                uos.remove(path)
        
        

        
