import uos

def __main__(args):

    if len(args) != 1:
        print("Remove directory, rmdir <path>")
        return
    else:
        path=args[0]

        try:
            uos.rmdir(path)
        except OSError:
            print("Invalid path")        
        

        
