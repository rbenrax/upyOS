import ugit

def __main__(args):

    if len(args) == 1 and args[0]=="--h":
        print("Upgrade upyOS from git repository\nUsage: upgrade")
        return
    else:

        #try:
        print("Upgrading from upyOS git repsitory, wait...")
        ugit.pull_all()
        #except OSError:
        #    print("Error on upgrade")
   
        

        
