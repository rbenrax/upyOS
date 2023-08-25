import uos

def __main__(args):

    if len(args) != 1:
        print("Chage current directory, cd <path>")
        return
    else:
        path=args[0]

        try:
            uos.chdir(path)
        except OSError:
            print("Invalid path")
   
        

        
