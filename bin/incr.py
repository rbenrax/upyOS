import utls
import sdata

def __main__(args):

    if len(args) == 0:
        print("Increase an env variable\nUsage: incr <var> [<incr>]:")
        return
    
    val = 0
    inc = 1

    var_name = args[0]

    if var_name not in sdata.sysconfig["env"]:
        utls.setenv(var_name, 0)  # Guardar como int

    tmp = utls.getenv(var_name)

    if isinstance(tmp, int):
        val = tmp
    else:
        print(f"Variable {var_name} is not an integer")
        return

    if len(args) == 2:
        try:
            inc = int(args[1])
        except ValueError:
            print(f"Increment value '{args[1]}' is not an integer")
            return

    utls.setenv(var_name, val + inc)