# Init file script in normal mode, if does not exists, we are in recovery mode and should exists init.rec

clear
py print("\033[1;33;44m",end="")
cat /etc/wellcome.txt
py print("\n\033[0m")

lshw.py -b

py print("\n\033[1mMemory:")
free

py print("\n\033[1mStorage:")
df

