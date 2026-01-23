import utls

def __main__(args):
    
    if len(args) == 0:
        print("Show files content/concatenate files\nUsage: cat <path1> <path2> ... <options>: -n (numbered lines) -f (filename)\n       cat <path1> <path2> >/>> <destpath>")
        return
    else:
        op=""
        mod=""
        paths=[]
        for a in args:
            if a in [">", ">>"]:
                op=a
                continue
            if op:
                paths.append(a)
                continue
            if a.startswith("-") and len(a) > 1 and not a[1].isdigit():
                mod+=a[1:]
                continue
            paths.append(a)
        
        if op:
            if not paths:
                print("Error: No destination path")
                return
            dest = paths.pop()
            fm="w"  #">"
            if op == ">>": fm="a" 
            with open(dest, fm) as out:
                for a in paths:
                    if not utls.file_exists(a) or utls.isdir(a):
                        print(f"File not exists {a}")
                        continue
                    with open(a, 'r') as f:
                        while True:
                            lin = f.readline()
                            if not lin: break
                            out.write(lin)
        else:
            for a in paths:
                if not utls.file_exists(a) or utls.isdir(a):
                    print(f"File not exists {a}")
                    continue
                lc=0
                with open(a, 'r') as f:
                    if "f" in mod:
                        print(f"{a}")
                    while True:
                        lin = f.readline()
                        if not lin: break
                        lc+=1
                        if "n" in mod:
                            print(f"{lc} {lin}", end="")
                        else:
                            print(f"{lin}", end="")
                    print("")

if __name__ == "__main__":
    args = ["/main.py", "/boot.py", "-nf"]
    __main__(args)