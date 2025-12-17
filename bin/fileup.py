import sdata
import utls

import sys

def __main__(args):
    
    if len(args) == 0:
        print ("Upload file from terminal\nUsage: fileup <filename>")
        return
    
    if utls.protected(args[0]):
        print("Can overwrite system file!")
        return
    
    print ("Paste file content and press CTRL+D to save.")
    
    try:
        with open(args[0], "wt") as fp:
            while True:
                line = sys.stdin.readline()
                if not line:
                    break
                fp.write(line)
        print("\nFile saved.")
    except Exception as e:
        print(f"Error saving file: {e}")
