
#print(sys.path)

import utime
import uos
import utls

def init():

    if not utls.file_exists("/etc"):
        uos.mkdir("/etc")

    name = "smolOS-" + uos.uname()[0]
    board = uos.uname()[4]
    
    if not utls.file_exists("/etc/" + name + ".board"):
        
        # Create/Load board config
        try:
            
            with open("/etc/" + name + ".board", "w") as cf:
                cf.write("Board=" + board + "\n")
                cf.write("Leds pins=" + "[25]" + "\n")
                cf.write("Speed range=" + '{"slow": 80, "turbo": 80}'+ "\n")
                cf.write("Turbo=" + "false" + "\n")
                cf.write("Aliases=" + '{"h": "help", "show": "cat", "remove": "rm", "edit": "vi", "list": "ls"}' + "\n")
            print("Board config generated, you may config before continue.")
        
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


        