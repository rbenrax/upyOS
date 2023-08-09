import sys
import sdata
import editor

#TODO: Prettify

def __main__(args):
    if len(args) == 0:
        print ("Usage:")
        print ("vi <file> ")
        return
    
    editor.edit(args[0])