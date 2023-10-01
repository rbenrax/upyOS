# Luncher and main.py clone for boot recovery
# Launch upyOS with grub the first time to generate the /etc .board file
# import grub
# grub.mbr()

# Launch upyOS once generated the .board file, aprox 0.5kb ram saved
import kernel
upyos = kernel.upyOS("") # Boot_args: -r
