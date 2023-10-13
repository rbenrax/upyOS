import sdata
import utime

def __main__(args):

    #print("This command should be analized, caos")
    #return

    if len(args) == 1:
        print("Show process status\nUsage: ps")
        return
    
    # Process status
    if len(sdata.procs)>0:
        print(f"  Proc Sts     Init_T   Elapsed   Thread_Id   Cmd/Args")
        for i in sdata.procs:
            print(f"{i.pid:6}  {i.sts:3}  {i.stt:8}  {utime.ticks_ms() - i.stt:8}  {i.tid:10}   {i.cmd} {" ".join(i.args)}")
