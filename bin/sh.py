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

def run(ssf, lbl_ln):
    line=0
    
    with open(ssf,'r') as f:

        skip_lines = 0
        ltf="" # Forward label to find
        
        while True:
            lin = f.readline()
            if not lin:
                if ltf!="": print(f"sh - Label {ltf} not found, ending")
                break
            
            line+=1

            if lbl_ln > 0 and line <= lbl_ln: # Skip lines for goto label command
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
                #print(ltf, cmdl[1:-1])
                if ltf==cmdl[1:-1]:  # -1 is carriage return at end of the line
                    #print("encontrada")
                    ltf=""
                
                labels[cmdl[1:-1]]=line # Save labels and his line
                #print(labels)
                continue # Lbels are not procesed
            
            if ltf != "": continue # looking for a label
            
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
            elif cmdl[:5] == "goto ":
                tmp = cmdl.split()
                acca = tmp[1]
                if not acca in labels:
                    ltf=acca
                    continue
                else:
                    lbl_ln=labels[acca]
                    return lbl_ln
            # Conditional execution: if $0 == 5 return (ex.)
            elif cmdl[:3] =="if ":
                tmp = cmdl.split()
                
                # Translate env vars
                for i, e in enumerate(tmp):
                    if e[0]=="$":
                        #print(e[0])
                        v=utls.getenv(e[1:])
                        #print(v)
                        tmp[i] =  v
                
                #print(sdata.sysconfig["env"])
                #print(tmp)
                            
                arg1 = tmp[1] # operand1
                op   = tmp[2] # operator
                arg2 = tmp[3] # operand2
                acc  = tmp[4] # action
                
                acca=""
                if len(tmp) > 5:
                    acca = tmp[5] # action arg
                    
                if arg1=="" or arg2=="" or acc=="":
                    print(f"sh - Invalid args: {cmdl[:-1]}")
                    print(f"sh - Values: {tmp}")
                    return 0
                
                #res = eval('"' + arg1 + '"' + op + '"' + arg2 + '"')
                #print(tmp)
                res = eval(arg1 + " " + op + " " + arg2)
                
                #print(f"{line}: {cmdl[:-1]} {res=}")

                if res: # Eval result
                    if acc == "goto":
                        if not acca in labels:
                            ltf=acca
                            continue
                        else:
                            lbl_ln=labels[acca]
                            return lbl_ln # return the label line number, and rerun the script 
                       
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
        lbl_ln=0 
        while True:
            lbl_ln = run(ssf, lbl_ln) # Call script once on every label
            # if lbl_ln = 0 then end the script
            # if lbl_ln <> 0 then goto statement in course
            if lbl_ln==0:
                break   
    else:
        print(f"{ssf}: script not found")


    
        

        

