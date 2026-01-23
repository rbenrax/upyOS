import uos
import utls

def protected(p):
    if utls.protected(p):
        print(f"Can not remove system file {p}")
        return True
    else:
        return False

def osremove(path):
    if utls.file_exists(path):
        uos.remove(path)
    else:
        print(f"not found: {path}")
        
def remove(path):
    if not utls.isdir(path):
        if not protected(path):
            osremove(path)
    else:
          r = input("remove all files in dir " + path + "? ")
          if r=="y":
                tmp=uos.listdir(path)
                for f in tmp:
                    full_p = path
                    if not full_p.endswith("/"):
                        full_p += "/"
                    full_p += f
                    
                    if not utls.isdir(full_p):
                        if not protected(full_p):
                            osremove(full_p)
                    else:
                        remove(full_p)
                
                # After emptying (or trying to), remove the directory itself
                if not protected(path):
                    try:
                        uos.rmdir(path)
                    except OSError:
                        # Directory might not be empty if files were protected
                        pass

def __main__(args):

    if len(args) == 0 or args[0]=="--h":
        print("Remove file or directory\nUsage: rm <path> ...")
        return
    else:
        for path in args:
            remove(path)
