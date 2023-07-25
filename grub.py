import utime
import sys

try:
    wait=5

    print("\033[2J")
    print("\033[H")
    print("\nsmolOS grub\n")
    for t in range(wait):
        print("\033[H     ")
        #print("\033[1J     ")
        print(t)
        utime.sleep(1)

    print("Booting smolOS...")

except KeyboardInterrupt:
     print("Grub canceled, smolOS booting aborted.")
     sys.exit()
     
