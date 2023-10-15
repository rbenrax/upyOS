import uos
import utls
import utime

def info(path="", mode="-l"):

    #print(f"{path}")
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

    if utls.protected(path):
        fattr += "r-"
    else:
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
        print(f"{fattr} {ssize} {utls.MONTH[localtime[1]]} {localtime[2]:0>2} " + \
              f"{localtime[3]:0>2}:{localtime[4]:0>2}:{localtime[5]:0>2} {filename}")
          
    return size


def ls(path="", mode="-l"):

    if "-" in path:
        mode = path
        path=""

    if "--h" in mode:
        print("List files and directories, ls <path> <options>, --h -lhasnk")
        print("-h: human readable, -a: incl. hidden, -s: subdirectories, -k: no totals, -n: no file details")
        return

    cur_dir=uos.getcwd()
    #print("0", cur_dir)
    
    tsize=0
    if utls.isdir(path):
        uos.chdir(path)
        
        if path=="" or path==".." : path=uos.getcwd()

        #print("1", path)
        
        if len(path)>0:
            if path[0]  !="/": path = "/" + path
            if path[-1] !="/": path+="/"

        #print("2", path)
        
        tmp=uos.listdir()
        tmp.sort()

        for file in tmp:
            tsize += info(path + file, mode)
            if "s" in mode and utls.isdir(path + file):
                print("\n" + path + file + ":")
                tsize += ls(path + file, mode)
                print("")
        
        uos.chdir(cur_dir)
        
        if not 'k' in mode:
            if 'h' in mode:
                print(f"\nTotal {path}: {utls.human(tsize)}")
            else:
                print(f"\nTotal {path}: {tsize} bytes")

    else:
        print("Invalid directory")
    #print("3", uos.getcwd())
    
    return tsize

def help():
    print("List files, ls <path> <options>: [-lahnk --h] (list, hidden, human, no details, no totals) ")
    
def __main__(args):

    path=""
    mode="-l"

    if len(args)>1:
        if "--h" in args:
            help()
            return

        path=args[0]
        mode=args[1]

    elif len(args)==1:
       path=args[0]
        
    ls(path, mode)

#if __name__ == "__main__":

#    args = ["", "-l"]
#    __main__(args)

