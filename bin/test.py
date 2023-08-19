
import time, sys, utls, sdata, uos

oldcmd=""

def ls(self, path="/", mode="-l"):

    uos.chdir("/bin")

    if "-" in path:
        mode = path
        path=""

    old_dir=uos.getcwd()
    print("0", old_dir)
    
    if utls.isdir(path):

        uos.chdir(path)
        
        tmp=uos.listdir()
        tmp.sort()
        
        tsize=0
        
        print("1", path)
        
        for file in tmp:

            print(file)
            tsize += 5
            #tsize += self.info(file, mode)
        
        uos.chdir(old_dir)
        
        if 'h' in mode:
            print(f"\nTotal: {utls.human(tsize)}")
        else:
            print(f"\nTotal: {tsize} bytes")

    else:
        print("Invalid directory")

    print("2", uos.getcwd())
# - - - - - -    

def __main__(args):
    
    print (f"Prueba de llamada {args}")

    #print(sys.modules)
    #time.sleep(1)
    
#    print(sdata.sysconfig)
#    a={"a":1, "b":2, "c": 3}
#    print(a)
#    for k, v in a.items():
#        if v == 2:
#            print(k)

    while True:
        try:
           
            global oldcmd
            
            user_input = input("\n" + "/" + " $: ")
            
            if user_input == "r":
                user_input=oldcmd
            
            print(user_input)
            
            oldcmd = user_input
            
        except KeyboardInterrupt:
             sys.exit()

        except EOFError:
             print("Send EOF")

        except Exception as ex:
            print("cmd error, " + str(ex))


if __name__ == "__main__":

    #args =["ls"]
    #__main__(args)
    ls("")
        