import sys
import sdata

def __main__(args):
    """remove module name"""
    try:
        del sys.modules[args[0]]
    except:
        pass
