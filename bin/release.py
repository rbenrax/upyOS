import uos

def __main__(args):

    if len(args) == 1 and args[0]=="--h":
        print("Create new release index file for upyOS upgrade\nUsage: release")
        return
    else:
        fd="/etc/upgrade.inf"
        fr=["/boot.py","/main.py"] # Files to include       
        fi=["system.conf"] # Files to avoid
        dr=["/bin","/lib","/libx","/etc"] # Direcrories to include
        with open(fd, "w") as fu:
            for f in fr:
                fu.write(f+"\n")
                
            for d in dr:
                tmp=uos.listdir(d)
                for f in tmp:
                    if f in fi: continue
                    print(d + "/" + f)
                    fu.write(d + "/" + f + "\n")
                    
        print(f"\nFile {fd} successful created, shoud to be uploaded to git repository")



        
