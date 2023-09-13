import utls
import sdata

proc=None

# Shell script conditional execution
# Basic language:
#
# if <arg1> <comparison operator> <arg2> <action>
#
# <args>: String constant and environment variables (ex: $0, $?, $path, etc)
# <comparison operator>: Like Python (==, <, >, etc)
# <action>:
#    - Any program o command to run (ls, etc.)
#    - An integer, the number of lines to skip, empty lines included
#    - keyword: return, end script execution

def __main__(args):

    if len(args) == 0:
        print("Execute shell script file\nUsage: sh <script file>")
        return
    
    ssf=args[0]
    
    # Run shell script
    line=0
    if utls.file_exists(ssf):
        with open(ssf,'r') as f:
            skip_lines=0
            while True:
                lin = f.readline()
                if not lin: break
                line+=1

                if skip_lines > 0:
                    skip_lines-=1
                    continue
                
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


                if cmdl[:6] =="return": break

                # Conditional execution: if $0 == 5 return (ex.)
                if cmdl[:3] =="if ":
                    tmp = cmdl.split()
                    arg1 = tmp[1]
                    op   = tmp[2]
                    arg2 = tmp[3]
                    acc  = tmp[4]
                    
                    res = eval('"' + arg1 + '"' + op + '"' + arg2 + '"')
                    #if sdata.debug:
                    #    print(f"{line}: {cmdl[:-1]} {res=}")

                    if res:
                        if acc == "return": break
                        elif acc.isdigit():
                            skip_lines=int(acc)
                            continue
                        else:
                            #if sdata.debug:
                            #    print(" ".join(tmp[4:]))
                            proc.syscall.run_cmd(" ".join(tmp[4:]))
                    continue

                proc.syscall.run_cmd(cmdl)
    else:
        print(f"{ssf}: script not found")


    
        

        
