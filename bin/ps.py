import kernel
import utime

def __main__(args):

    print("This command should be analized, caos")
    return

    if len(args) == 1:
        print("Show process status\nUsage: ps")
        return
    
     # Process status
    if len(kernel.procs)>0:
        print(f"Proc Sts  Init_T   Elapsed   Thread_Id      Cmd/Args")
        
        for i in kernel.procs:
            print(f"{i.pid:4}  {i.sts}   {i.stt}  {utime.ticks_ms() - i.stt}      {i.tid}    {i.cmd} {" ".join(i.args)}")