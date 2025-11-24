import uos
import time
import sdata
import utls
import hashlib

def hash_sha1(filename):
    h = hashlib.sha1()
    with open(filename, 'rb') as f:
        while True:
            chunk = f.read(512)
            if not chunk:
                break
            h.update(chunk)
    return h.digest().hex()
    
def __main__(args):
    
    def fsize(fp):
        stat = utls.get_stat(fp)            
        return stat[6]

    if len(args) == 1 and args[0]=="--h":
        print("Create new release index file for upyOS upgrade\nUsage: release")
        return
    else:
        fd="/etc/upgrade.inf" # Realease file
        fr=["/boot.py","/main.py"] # Files to include       
        fi=["system.conf", "upgrade.inf", "upgrade2.inf", "ptf_file.tmp"] # Files to avoid
        dr=["/bin","/lib","/libx","/etc"] # Direcrories to include
        
        cont=0
        with open(fd, "w") as fu:
            t = time.localtime()
            ver = f"#upyOS,{sdata.version},{t[0]}-{t[1]:02d}-{t[2]:02d}"
            fu.write(ver + "\n")
            print(ver)
                
            for f in fr:
                fu.write(f + "," + str(fsize(f)) + "," + hash_sha1(f) + "," + "\n")
                print(f)
                cont+=1
                
            for d in dr:
                tmp=uos.listdir(d)
                for f in tmp:
                    if f in fi: continue
                    fp = d + "/" + f
                    print(fp)
                    fu.write(fp + "," + str(fsize(fp)) + "," + hash_sha1(fp) + "," + "\n")
                    cont+=1
                    
            ls = f"#files,{cont}"
            print(ls)
            fu.write(ls + "\n")
            
        print(f"\nRelease file {fd} successful created with {cont} files, shoud to be uploaded to github repository")

if __name__ == "__main__":
    __main__([""])
    
