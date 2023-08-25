import micropython
import sdata

def __main__(args):
    
    if len(args)==1:
        opt=args[0]

        if opt=="--h":
            print("Print memory information\nUsage: mi <opt>, 0,1,")
            return
        
        print(micropython.mem_info(opt))
    else:
        print(micropython.mem_info())
