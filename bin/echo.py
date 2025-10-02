import utls

# This command allows you to redirect the output to an environment variable.
# Afterwards, it is possible to send it to a file using the 'touch' command: "touch <filename> <var, ...>"
def __main__(args):
    if len(args) > 0:
        if ">>" in args or ">" in args:
            try:
                # Detectar operador y modo de apertura
                if ">>" in args:
                    idx, mode = args.index(">>"), "a"
                else:
                    idx, mode = args.index(">"), "w"

                # Validar destino
                if idx + 1 >= len(args):
                    print("Error: falta destino después de '>'")
                    return

                target = args[idx + 1]
                
                # Redirigir a archivo
                if "." in target or "/" in target:
                    with open(target, mode) as f:
                        f.write("".join(args[:idx]) + "\n")
                else:
                    # Redirigir a "variable de entorno"
                    if mode == "a":
                        current = str(utls.getenv(target))
                        utls.setenv(target, current + "".join(args[:idx]))
                    else:
                        utls.setenv(target, "".join(args[:idx]))

            except Exception as e:
                print(f"Error redir: {e}")
                return

        else:
            print("".join(args))
    else:
        print("Show msg + env variable\nUsage: echo const/<var> [>[>] <var>/<file>]")