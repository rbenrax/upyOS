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
labels={}

def run(ssf, label):
    print(ssf)
    line=0
    with open(ssf,'r') as f:

        skip_lines = 0
            
        while True:
            lin = f.readline()
            if not lin: break
            line+=1

            if label > 0 and line <= label: # Skip lines in goto
                continue

            if skip_lines > 0: # Skip lies in skip
                skip_lines-=1
                continue
            
            if lin.strip()=="": continue
            if len(lin)>0 and lin[0]=="#": continue
            cmdl=lin.split("#")[0] # Left part of commented line
            
            global labels
            #print(cmdl)
            if cmdl[0]==":":
                labels[cmdl[1:-1]]=line # Save labels and his line
                #print(labels)
                continue
            
            # Unconditional commands
            # End script
            if cmdl[:6] =="return": break

            # Skip lines
            if cmdl[:5] =="skip ":
                tmp = cmdl.split()
                acca = tmp[1]
                if acca.isdigit():
                   skip_lines=int(acca)
                   continue

            # Conditional execution: if $0 == 5 return (ex.)
            if cmdl[:3] =="if ":
                tmp = cmdl.split()
                # Translate env vars
                for i, e in enumerate(tmp):
                    if e[0]=="$":
                        v=proc.syscall.getenv(e[1:])
                        tmp[i] = v
                        
                arg1 = tmp[1] # operand1
                op   = tmp[2] # operator
                arg2 = tmp[3] # operand2
                acc  = tmp[4] # action
                
                acca=""
                if len(tmp) > 5:
                    acca = tmp[5] # action arg
                    
                res = eval('"' + arg1 + '"' + op + '"' + arg2 + '"')
                #if sdata.debug:
                #    print(f"{line}: {cmdl[:-1]} {res=}")

                if res:
                    if acc == "goto":
                        label=labels[acca]
                        return label
                       
                    if acc == "return": break
                    elif acc=="skip" and acca.isdigit():
                        skip_lines=int(acca)
                        continue
                    elif acc=="run":
                        proc.syscall.run_cmd(" ".join(tmp[5:]))
                    else:
                        #if sdata.debug:
                        #    print(" ".join(tmp[4:]))
                        proc.syscall.run_cmd(" ".join(tmp[4:]))
                continue

            proc.syscall.run_cmd(cmdl)
            
        return 0


def __main__(args):

    if len(args) == 0:
        print("Execute shell script file\nUsage: sh <script file>")
        return
    
    ssf=args[0]
    
    # Run shell script
    if utls.file_exists(ssf):
        label=0
        while True:
            ret = run(ssf, label) # Call script once on every label
            if ret==0:
                break
            else:
                label=ret
    else:
        print(f"{ssf}: script not found")


    
        

        
