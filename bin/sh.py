import utls

proc=None

def __main__(args):

    if len(args) == 0:
        print("Execute shell script file\nUsage: sh <script file>")
        return
    
    ssf=args[0]
    
    # Run shell script
    if utls.file_exists(ssf):
        with open(ssf,'r') as f:
            while True:
                lin = f.readline()
                if not lin: break

                if lin.strip()=="": continue
                if len(lin)>0 and lin[0]=="#": continue
                cmdl=lin.split("#")[0] # Left comment line part
                
                # Translate env variables $*
                tmp = cmdl.split()
                
                if not tmp[0] in ["export", "echo", "unset"]:
                    for e in tmp:
                        if e[0]=="$":
                            v=proc.syscall.getenv(e[1:])
                            cmdl = cmdl.replace(e, v)

                proc.syscall.run_cmd(cmdl)
    else:
        print(f"{ssf}: script not found")


    
        

        
