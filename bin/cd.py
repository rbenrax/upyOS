import uos

def __main__(args):

    if "--h" in args:
        print("Change current directory\nUsage: cd <path>")
        return

    if len(args) == 0:
        uos.chdir('/')
        
    elif len(args) == 1:
        path=args[0]

        try:
            uos.chdir(path)
        except OSError:
            print("Invalid path")