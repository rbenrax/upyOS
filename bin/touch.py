import sys
import sdata

def __main__(args):

    if len(args) == 0:
        print ("Usage:")
        print ("touch <filename> <line content..>, Create or add a line to a file with values passed")
        return
    
    with open(args[0], "a") as file:
        for a in args[1:]:
            file.write(a + " ")
        file.write("\n")
