import utime
import sys

try:
    wait=5

    print("\033[2J") # Clear screen
    print("\033[H")  # Goto 0,0
    
    print("\nsmolOS grub\n")
    for t in range(wait):
        print("\033[4;1H")
        print(t)
        utime.sleep(1)

    print("Booting smolOS...")

except KeyboardInterrupt:
     print("Grub canceled, smolOS booting aborted.")
     sys.exit()
     
