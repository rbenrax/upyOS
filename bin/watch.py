import utime
import sdata

# Proc ref passed in call
proc = None

def __main__(args):
    if len(args) == 0:
        print("Repeat a command every specified time\nUsage: watch [-t <time>] [-q] <cmd> <args...>")
        return

    t = 2.0
    quiet = False
    cmd_start = -1

    # Parsear argumentos hasta encontrar el primer no-flag
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "-t":
            if i + 1 >= len(args):
                print("Error: -t requires a numeric argument")
                return
            try:
                t = float(args[i + 1])
                if t <= 0:
                    print("Error: time must be positive")
                    return
            except ValueError:
                print("Error: -t requires a numeric argument")
                return
            i += 2
        elif arg == "-q":
            quiet = True
            i += 1
        elif arg.startswith("-"):
            # Flag desconocido
            print(f"Error: unknown flag '{arg}'")
            return
        else:
            # Primer argumento que no es flag → inicio del comando
            cmd_start = i
            break
    else:
        # No se encontró ningún comando (todos fueron flags o no hay args)
        print("Error: missing command to execute")
        return

    cmd = " ".join(args[cmd_start:])

    while True:
        if proc.sts == "S":
            break
        if proc.sts == "H":
            utime.sleep(1)
            continue

        if not quiet:
            print(f"\033[2J\033[HEvery: {t}s: {cmd}")
        
        sdata.upyos.run_cmd(cmd)
        utime.sleep(t)