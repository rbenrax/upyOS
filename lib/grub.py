
#print(sys.path)

import utime
import uos
import utls
import sysdata

def init():

    if not utls.file_exists("/etc"):
        uos.mkdir("/etc")

    # Create sysconfig
    try:

        name = "smolOS-" + uos.uname()[0]
        board = uos.uname()[4]
        sco = sysdata.SysData(board)
        
        if not utls.file_exists("/etc/" + name + ".board"):
            with open("/etc/" + name + ".board", "w") as bcf:
                utls.dump(sco.getBoard(), bcf)

            print("Board config generated, you may config before continue.")
            
        if not utls.file_exists("/etc/system.conf"):
            with open("/etc/system.conf", "w") as scf:
                utls.dump(sco.getSysConf(), scf)

            print("Sysconf creado.")
            
    
    except Exception as ex:
        print(ex)

try:
    wait=5

    print("\033[2J") # Clear screen
    print("\033[H")  # Goto 0,0
    print("smolOS grub\n")
    
    print("Initializing...")
    init()
    
    for t in range(wait):
        print("\033[5;0H")
        print(t)
        utime.sleep(1)

    print("Booting smolOS...")
    import smolos
    
except KeyboardInterrupt:
     print("Grub canceled, smolOS booting aborted.")
     sys.exit()
     
#except Exception as ex:
#     print("Error: " + ex)


        