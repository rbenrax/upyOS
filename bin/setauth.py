import sdata
import utls

def __main__(args):
    
    if len(args) == 0 or args[0]=="--h":
        print("Set/view user name and  set password\nUsage: setauth <username> <password> <repeat password>: -v view username -d disable auth")
        print("user name and password are stored in /etc/system.conf and are valid for telent and ftp services")
        print('if password is empty or -d, then the security access is disabled')
        return
    
    elif len(args) == 3:
        
        if args[0].strip() == "":
            print("User name is not valid")
            return
        
        if args[1] != args[2]:
            print("Passwords are not the same")
            return
        
        sdata.sysconfig["auth"]["user"]  = args[0]
        sdata.sysconfig["auth"]["paswd"] = args[1].strip()
        
        utls.save_conf_file(sdata.sysconfig, "/etc/system.conf")
        
        if args[1].strip() == "":
            print(f"Security has been disabled")
        else:
            print(f"New password has been set fot user {args[0]}")
            
        #TODO: Save file
        
    elif len(args) == 1:
        if args[0] == "-v":
            print(f"Curren user is {sdata.sysconfig["auth"]["user"]}")
            
        elif args[0] == "-d":
            sdata.sysconfig["auth"]["passwd"] = ""
            utls.save_conf_file(sdata.sysconfig, "/etc/system.conf")
            print(f"Security has been disabled")
            
        #TODO: Save file
    else:
        print(f"Invalid arguments")
            
        