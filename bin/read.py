import utls

def __main__(args):
    
    if len(args) < 2:
        print("Accept data from console and store in a env var\nUsage: read <envvar> <prompt>")
        return
    else:
        dta = input(args[1])
        utls.setenv(args[0], dta)