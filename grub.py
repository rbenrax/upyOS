import utime
wait=5
print("\033[2J\n")
print("smolOS grub\n")
for t in range(wait):
    print("\033[H     ")
    #print("\033[1J     ")
    print(t)
    utime.sleep(1)

print("Booting smolOS...")