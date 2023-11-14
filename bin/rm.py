import uos
import utls

def protected(p):
    if utls.protected(p):
        print(f"Can not remove system file {p}")
        return True
    else:
        False

def remove(path):
    if not utls.isdir(path):
        if not protected(path):
            uos.remove(path)
    else:
          r = input("remove all files in dir " + path + "? ")
          if r=="y":
               tmp=uos.listdir(path)
               for f in tmp:
                   if not utls.isdir(f):
                       if not protected(f):
                           uos.remove(path + "/" + f)
                   else:
                       remove(path + "/" + f)

def __main__(args):

    if len(args) == 0 or args[0]=="--h":
        print("Remove file\nUsage: rm <path> ...")
        return
    else:
        for path in args:
            remove(path)
        
