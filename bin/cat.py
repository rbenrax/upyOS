import utls

def __main__(args):
    
    if len(args) == 0:
        print("Show files content/concatenate files\nUsage: cat <path1> <path2> ...\n       cat <path1> <path2> >/>> <destpath>")
        return
    else:
        op=""
        for a in args:
            if a in [">", ">>"]:
                op=a
                break
            else:
                if not utls.file_exists(a):
                    print(f"File not exists {a}")
                    return
        
        if op:
            fm="w"  #">"
            if op == ">>": fm="a" 
            with open(args[-1], fm) as out:
                for a in args:
                    if a == op: break
                    #print(a)
                    with open(a, 'r') as f:
                        while True:
                            lin = f.readline()
                            if not lin: break
                            out.write(lin)
                        out.write("\n")
                        #TODO: remove a \n at end 
        else:
            for a in args:
                print("--" + a)
                with open(a, 'r') as f:
                    while True:
                        lin = f.readline()
                        if not lin: break
                        print(lin, end="")
                    print("")

if __name__ == "__main__":
    args = ["/main.py", "/boot.py"]
    #args = ["/main.py", "/boot.py", ">>", "/out.txt"]
    __main__(args)