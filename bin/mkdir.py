import uos

def __main__(args):

    if len(args) != 1:
        print("Make directory\nUsage: mkdir <path>")
        return
    else:
        path=args[0]

        try:
            uos.mkdir(path)
        except OSError:
            print("Invalid path")        
        

        
