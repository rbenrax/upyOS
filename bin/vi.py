import sys
import sdata
import editor

#TODO: Prettify

def __main__(args):
    if len(args) == 0:
        print ("Edit a file\nUsage: vi <filename>")
        return
    
    editor.edit(args[0])
    del sys.modules["editstr"]
    del sys.modules["terminal"]
    del sys.modules["editor"]