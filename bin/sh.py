import utls
import sdata

proc=None

# Shell script conditional execution
# Basic language:
#
# if <arg1> <comparison operator> <arg2> <action> <action arg>
#
# <args>: String constant and environment variables (ex: $0, $?, $path, etc)
# <comparison operator>: Like Python (==, <, >, etc)
# <action>:
#    - run and/or the program o command to run (ls, etc.)
#    - skip and an integer, the number of lines to skip, empty lines included
#    - return, end script execution 
#    - allowed labels (:label) and goto command
#
# unconditional, skip n, return and goto
#

labels={}

def run(ssf, label):
    line=0
    with open(ssf,'r') as f:

        skip_lines = 0
            
        while True:
            lin = f.readline()
            if not lin: break
            line+=1

            if label > 0 and line <= label: # Skip lines for goto label command
                continue

            if skip_lines > 0: # Skip lines forward in skip command
                skip_lines-=1
                continue
            
            if lin.strip()=="": continue   # Empty lines skipped
            if len(lin)>0 and lin[0]=="#": continue # Commanted lines skipped
            cmdl=lin.split("#")[0] # Left part of commented line
            
            global labels
            #print(cmdl)
            if cmdl[0]==":":
                labels[cmdl[1:-1]]=line # Save labels and his line
                #print(labels)
                continue
            
            # Unconditional commands
            # End script
            if cmdl[:6] =="return": 
                break
            # Skip lines
            elif cmdl[:5] =="skip ":
                tmp = cmdl.split()
                acca = tmp[1]
                if acca.isdigit():
                   skip_lines=int(acca)
                   continue
            # Goto :label
            elif cmdl[:5 == "goto ":
                tmp = cmdl.split()
                acca = tmp[1]            
                label=labels[acca]
                return label
            # Conditional execution: if $0 == 5 return (ex.)
            elif cmdl[:3] =="if ":
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

                if res: # Eval result
                    if acc == "goto":
                        label=labels[acca]
                        return label # return the label line number, and rerun the script 
                       
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
    
    # Run shell script file
    if utls.file_exists(ssf):
        label=0 
        while True:
            label = run(ssf, label) # Call script once on every label
            # if label = 0 then end the script
            # if label <> 0 then goto statement in course
            if label==0:
                break   
    else:
        print(f"{ssf}: script not found")


    
        

        
