import utls
import sdata

def __main__(args):

    if len(args) == 0:
        print("Check if file/directory/proc exists\nUsage: test -p <proccess name> -f/-d <path> [> <var>]")
    else:

        ret = False
        if "-f" in args:
            ret = utls.file_exists(args[1])

        if "-d" in args:
            ret = utls.isdir(args[1])

        if "-p" in args:
            pn = args[1]
            for i in sdata.procs:
                if pn in i.cmd:
                    ret=True
                    break

        if not utls.redir(args, ret):
            print(ret)