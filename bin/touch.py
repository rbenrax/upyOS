import sys
import sdata

def __main__(args):

    if len(args) == 0:
        print ("Create and/or add a line to a file with values in line\nUsage: touch <filename> <line content..>")
        return
    
    with open(args[0], "a") as file:
        for a in args[1:]:
            file.write(a)
        file.write("\n")
