import sdata

def __main__(args):
    
    if len(args) == 0:
        print ("Usage:")
        print ("lineup <file>, upload file in line mode,")
        print ("empty line to end upload")
        return
    
    with open(args[0], "wt") as fp:
      while (True):
        line = input(">")
        #for c in line:
        #   print(hex(ord(c)))
        if not line:
            break
        fp.write(line + "\n")
