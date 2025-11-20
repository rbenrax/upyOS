import uos
import time
import sdata
import utls

def __main__(args):
    
    def fsize(fp):
        stat = utls.get_stat(fp)            
        return stat[6]

    if len(args) == 1 and args[0]=="--h":
        print("Create new release index file for upyOS upgrade\nUsage: release")
        return
    else:
        fd="/etc/upgrade2.inf" # Realease file
        fr=["/boot.py","/main.py"] # Files to include       
        fi=["system.conf", "upgrade.inf", "upgrade2.inf"] # Files to avoid
        dr=["/bin","/lib","/libx","/etc"] # Direcrories to include
        
        cont=0
        with open(fd, "w") as fu:
            t = time.localtime()
            ver = f"#upyOS,{sdata.version},{t[0]}-{t[1]:02d}-{t[2]:02d}"
            fu.write(ver + "\n")
            print(ver)
                
            for f in fr:
                fu.write(f + "," + str(fsize(f)) + "\n")
                print(f)
                cont+=1
                
            for d in dr:
                tmp=uos.listdir(d)
                for f in tmp:
                    if f in fi: continue
                    fp = d + "/" + f
                    print(fp)
                    fu.write(fp + "," + str(fsize(fp)) + "\n")
                    cont+=1
                    
            ls = f"#files,{cont}"
            print(ls)
            fu.write(ls + "\n")
            
        print(f"\nRelease file {fd} successful created with {cont} files, shoud to be uploaded to github repository")

if __name__ == "__main__":
    __main__([""])
    
