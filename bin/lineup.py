import sdata

def __main__(args):
    
    if len(args) == 0:
        print ("Usage:")
        print ("lineup <file>, upload file in line mode,")
        print ("empty line to end upload")
        return
    
    with open(args[0], "wt") as fp:
      while (True):
        try:
            line = input(">")
            fp.write(line + "\n")
        except EOFError:
            break
