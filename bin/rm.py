import uos
import utls

def remove(path):
    if not utls.isdir(path):
         uos.remove(path)
    else:
          r = input("remove all files in dir " + path + "? ")
          if r=="y":
               tmp=uos.listdir(path)
               for f in tmp:
                   if not utls.isdir(f):
                       uos.remove(path + "/" + f)
                   else:
                       remove(path + "/" + f)

def __main__(args):

    if len(args) == 0 or args[0]=="--h":
        print("Remove file\nUsage: rm <path>")
        return
    else:
        for path in args:
            if utls.protected(path):
                print(f"Can not remove system file {path}")
            else:
                remove(path)
        