import sdata

def __main__(args):
   for k, v in sdata.sysconfig["env"].items():
       print(f'{k}={v}')
                
