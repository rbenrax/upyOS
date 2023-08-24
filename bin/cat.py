
def __main__(args):
    
    if len(args) == 0:
        print("Show file content, cat <path>")
        return
    else:
        with open(args[0], 'r') as f:
            while True:
                lin = f.readline()
                if not lin: break
                print(lin, end="")

#if __name__ == "__main__":

#    args = ["/main.py"]
#    __main__(args)