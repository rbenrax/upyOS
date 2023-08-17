import uos
import utls

def __main__(args):

    mode="-n"

    if len(args) == 1:
        mode=args[0]
    
    if mode == "--h":
        print("Change to/from recovery mode, recovery <options>: options --h -n -r")
        return
    
    nor = "/etc/init.sh"
    rec = "/etc/init.rc"
    
    if mode == "-n":
        if utls.file_exists(rec):
            if utls.file_exists(nor):
                uos.remove(nor)
            uos.rename(rec, nor)
            print("Set Normal node boot")
            return
        else:
            print(rec + " not exists")
        
    if mode == "-r":
        if utls.file_exists(nor):
            if utls.file_exists(rec):
                uos.remove(rec)
            uos.rename(nor, rec)
            print("Set Recovery node boot")
        else:
            print(nor + " not exists")

if __name__ == "__main__":

    args =["-n"]
    __main__(args)
        
