import utls

def __main__(args):
    
    if len(args) == 0:
        print("Show files content/concatenate files\nUsage: cat <path1> <path2> ... <options>: -n (numbered lines) -f (filename)\n       cat <path1> <path2> >/>> <destpath>")
        return
    else:
        op=""
        mod=""
        for a in args:
            if a in [">", ">>"]:
                op=a
                break
            elif a[0] == "-":
                mod=a
                continue
            else:
                if not utls.file_exists(a) or utls.isdir(a):
                    print(f"File not exists {a}")
                    return
        
        if op:
            fm="w"  #">"
            if op == ">>": fm="a" 
            with open(args[-1], fm) as out:
                for a in args:
                    if "-" in a: continue
                    if a == op: break
                    #print(a)
                    with open(a, 'r') as f:
                        while True:
                            lin = f.readline()
                            if not lin: break
                            out.write(lin.rstrip('\n'))
                        out.write("\n") 
        else:
            for a in args:
                if "-" in a: continue
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
    #args = ["/main.py", "/boot.py", ">", "/out.txt"]
    __main__(args)