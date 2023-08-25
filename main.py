# Launch smolOS with grub the first time to generate the /etc .board file
# import grub
# grub.mbr()

# Launch smolOS once generated the .board file, aprox 0.5kb ram saved
import smolos
smol = smolos.smolOS()