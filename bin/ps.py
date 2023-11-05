import utime
import sdata
import utls

def __main__(args):

    #print("This command should be analized, caos")
    #return

    if len(args) == 1:
        print("Show process status\nUsage: ps")
        return
    
    # Process status
    if len(sdata.procs)>0:
        print(f"  Proc Sts    Init_T       Elapsed   Thread_Id   Cmd/Args")
        for i in sdata.procs:
            print(f"{i.pid:6}  {i.sts:3} {utls.time2s(i.stt, "n"):8} {utls.time2s(utime.time() - i.stt, "e"):8}  {i.tid:10}   {i.cmd} {" ".join(i.args)}")
 