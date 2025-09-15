import sdata

def __main__(args):
   for k, v in sdata.sysconfig["env"].items():
       #print(f'{k}={v}')
       if isinstance(v, str):
           print(f"{k}='{v}'")
       else:
           print(f"{k}={v}")

                
