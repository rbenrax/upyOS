import utls
import sdata

def __main__(args):

    if len(args) == 0:
        print("Decrease an env variable\nUsage: decr <var> [<decr>]:")
        return
    
    val = 0
    dec = 1

    var_name = args[0]

    if var_name not in sdata.sysconfig["env"]:
        utls.setenv(var_name, 0)  # Inicializar como entero

    tmp = utls.getenv(var_name)

    if isinstance(tmp, int):
        val = tmp
    else:
        print(f"Variable {var_name} is not an integer")
        return

    if len(args) == 2:
        try:
            dec = int(args[1])
        except ValueError:
            print(f"Decrement value '{args[1]}' is not an integer")
            return

    utls.setenv(var_name, val - dec)
