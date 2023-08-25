import sdata
import uos

def __main__(args):
    
    print(sdata.name + " version: " + sdata.version + "\n")

    with open("/etc/help.txt", 'r') as f:
        while True:
            lin = f.readline()
            if not lin: break
            print(lin, end="")
        print("")

    print("External commands:\n")
    
    tmp=uos.listdir("/bin")
    tmp.sort()
    buf=""
    for ecmd in tmp:
        if ecmd.endswith(".py"):
            buf += ecmd[:-3] + ", "
        else:
            buf += ecmd + ", "
    
    print(buf[:-2])
