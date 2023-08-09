
#print(sys.path)

import sys
import utime
import uos
import utls
import syscfg

def init():

    if not utls.file_exists("/etc"):
        uos.mkdir("/etc")

    # Create sysconfig

    file = "/etc/smolOS-" + uos.uname()[0] + ".board"
    board = uos.uname()[4]
    sco = syscfg.SysCfg(board)
    
    if not utls.file_exists(file):
        utls.save_conf_file(sco.getBoard(), file)
        print("Board config generated, you may config before continue.")
        
    if not utls.file_exists("/etc/system.conf"):
        utls.save_conf_file(sco.getSysConf(), "/etc/system.conf")
        print("Sysconf creado.")
    
try:
    wait=2

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
     
except Exception as ex:
    print(ex)
    #sys.print_exception()

        