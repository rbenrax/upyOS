import uos
import utls
import utime

def info(path="", mode="-l"):

    print(f"{path}")
    if not utls.file_exists(path):
        print("File not found")
        return
    
    filename= path.split("/")[-1]
    
    # Hidden files
    if not "a" in mode:
        if filename[0]==".": return 0
    
    stat = utls.get_stat(path)
    
    #mode = stat[0]
    size = stat[6]
    mtime = stat[8]
    localtime = utime.localtime(mtime)

    if utls.isdir(path):
        fattr= "d"
    else:
        fattr= " "

#    if utls.protected(path):
#        fattr += "r-"
#    else:
        fattr += "rw"

    if ".py" in path or ".sh" in path:
        fattr += 'x'
    else:
        fattr += '-'
    
    if "h" in mode:
        ssize = f"{utls.human(size)}"
    else:
        ssize = f"{size:7}"
        
    if not "n" in mode:
        print(f"{fattr} {ssize} {utls.MONTH[localtime[1]]} " + \
              f"{localtime[2]:0>2} {localtime[4]:0>2} {localtime[5]:0>2} {filename}")
          
    return size

def __main__(args):

    if len(args) == 0:
        print("Show file info, fi <path> <options>: [-ahn] (hidden, human, no details ) ")
        return

    path=""
    mode=""
    
    if len(args) == 1:
       path=args[0]
    elif len(args) > 1:
        path=args[0]
        mode=args[1]
        
    info(path, mode)
    
if __name__ == "__main__":

    args = ["/main.py", "-lha"]
    __main__(args)
