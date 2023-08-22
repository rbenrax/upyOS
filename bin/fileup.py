import sdata
import utls

def __main__(args):
    
    if len(args) == 0:
        print ("Usage:")
        print ("fileup <file>, upload file in line mode")
        return
    
    if utls.protected(args[0]):
        print("Can overwrite system file!")
        return
    
    print ("Send CTRL+D to end upload")
    with open(args[0], "wt") as fp:
      while (True):
        try:
            line = input(">")
            fp.write(line + "\n")
        except EOFError:
            break
