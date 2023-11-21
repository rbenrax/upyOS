import uos

def __main__(args):

    if len(args) == 1 and args[0]=="--h":
        print("Create new release of upyOS\nUsage: release")
        return
    else:
        fr=["/boot.py","/main.py"]        
        fi=["system.conf","init.sh","end.sh"]
        dr=["/bin","/lib","/libx","/etc"]
        with open("/etc/upgrade.inf", "w") as fu:
            for f in fr:
                fu.write(f+"\n")
                
            for d in dr:
                tmp=uos.listdir(d)
                for f in tmp:
                    if f in fi: continue
                    print(d + "/" + f)
                    fu.write(d + "/" + f + "\n")
            



        
