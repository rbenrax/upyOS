import utls
import sdata

# Shell script executor for upyOS
# Optimized for low ROM/RAM MCUs by reading line by line.

def run(ssf, args=[]):
    """Executes a shell script file line by line."""
    labels = {} # Cache for label line numbers
    
    # Environment variables for the script ($0, $1, etc.)
    # $0 is the script name, $1... are positional arguments
    utls.setenv("0", ssf)
    for i, arg in enumerate(args):
        utls.setenv(str(i+1), arg)

    try:
        with open(ssf, 'r') as f:
            line_num = 0
            skip_lines = 0
            
            while True:
                lin = f.readline()
                if not lin:
                    break
                
                line_num += 1
                
                # Check for skip_lines first
                if skip_lines > 0:
                    skip_lines -= 1
                    continue
                
                raw_lin = lin.strip()
                if not raw_lin or raw_lin.startswith("#"):
                    continue

                # Remove trailing comments
                cmdl_parts = raw_lin.split(" #", 1)
                cmd_string = cmdl_parts[0].strip()
                
                if not cmd_string:
                    continue

                # Process labels
                if cmd_string.startswith(":"):
                    lbl_name = cmd_string[1:].strip()
                    labels[lbl_name] = line_num
                    continue

                # Parse command line using shlex
                tokens = utls.shlex(cmd_string)
                if not tokens:
                    continue

                # Environment variable substitution for all tokens
                for i, t in enumerate(tokens):
                    if t.startswith("$"):
                        tokens[i] = str(utls.getenv(t[1:]))

                cmd = tokens[0]

                # Special built-in shell commands
                if cmd == "return":
                    break
                
                elif cmd == "skip":
                    if len(tokens) > 1 and tokens[1].isdigit():
                        skip_lines = int(tokens[1])
                    continue
                
                elif cmd == "goto":
                    if len(tokens) > 1:
                        target = tokens[1]
                        if target.startswith(":"): target = target[1:]
                        
                        if target in labels:
                            # Jump back or forward to known label
                            target_line = labels[target]
                            f.seek(0)
                            line_num = 0
                            for _ in range(target_line):
                                f.readline()
                                line_num += 1
                        else:
                            # Forward scan for label
                            found = False
                            while True:
                                flin = f.readline()
                                if not flin: break
                                line_num += 1
                                fs = flin.strip()
                                if fs.startswith(":") and fs[1:].strip() == target:
                                    labels[target] = line_num
                                    found = True
                                    break
                                elif fs.startswith(":"):
                                    labels[fs[1:].strip()] = line_num
                            
                            if not found:
                                print(f"sh: '{ssf}' line {line_num}: label '{target}' not found")
                                break
                    continue

                elif cmd == "if":
                    # if <arg1> <op> <arg2> <action> [action_args...]
                    if len(tokens) < 5:
                        print(f"sh: '{ssf}' line {line_num}: invalid 'if' syntax")
                        continue
                    
                    arg1, op, arg2, action = tokens[1], tokens[2], tokens[3], tokens[4]
                    action_args = tokens[5:] if len(tokens) > 5 else []

                    # Helper to convert values to numeric if possible
                    def conv(v):
                        try:
                            if "." in v: return float(v)
                            return int(v)
                        except:
                            return v

                    v1, v2 = conv(arg1), conv(arg2)
                    res = False
                    try:
                        if op == "==": res = (v1 == v2)
                        elif op == "!=": res = (v1 != v2)
                        elif op == "<":  res = (v1 < v2)
                        elif op == ">":  res = (v1 > v2)
                        elif op == "<=": res = (v1 <= v2)
                        elif op == ">=": res = (v1 >= v2)
                        elif op == "in": res = (str(v1) in str(v2))
                    except Exception as e:
                        print(f"sh: '{ssf}' line {line_num}: eval error: {e}")
                        continue
                    
                    if res:
                        # Handle the action
                        if action == "goto":
                            if not action_args: continue
                            target = action_args[0]
                            if target.startswith(":"): target = target[1:]
                            
                            if target in labels:
                                target_line = labels[target]
                                f.seek(0)
                                line_num = 0
                                for _ in range(target_line):
                                    f.readline()
                                    line_num += 1
                            else:
                                found = False
                                while True:
                                    flin = f.readline()
                                    if not flin: break
                                    line_num += 1
                                    fs = flin.strip()
                                    if fs.startswith(":") and fs[1:].strip() == target:
                                        labels[target] = line_num
                                        found = True
                                        break
                                    elif fs.startswith(":"):
                                        labels[fs[1:].strip()] = line_num
                                if not found:
                                    print(f"sh: '{ssf}' line {line_num}: label '{target}' not found")
                                    break
                            continue
                        
                        elif action == "return":
                            break
                        elif action == "skip":
                            if action_args and action_args[0].isdigit():
                                skip_lines = int(action_args[0])
                            continue
                        elif action == "run":
                            sdata.upyos.run_cmd(" ".join(action_args))
                        else:
                            # Default: the action is the command itself
                            sdata.upyos.run_cmd(" ".join(tokens[4:]))
                    continue

                # Default: regular command execution
                sdata.upyos.run_cmd(cmd_string)

    except Exception as e:
        print(f"sh: error executing '{ssf}': {e}")

def __main__(args):
    if not args:
        print("Execute shell script file\nUsage: sh <script file> [args...]")
        return
    
    ssf = args[0]
    if utls.file_exists(ssf):
        run(ssf, args[1:])
    else:
        print(f"sh: {ssf}: script not found")
