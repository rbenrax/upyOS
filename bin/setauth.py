import sdata
import utls

def __main__(args):
   
    doc = """
    USER AUTHENTICATION MANAGEMENT

    Usage:
      setauth <username> <password> <repeat_password>  Set username and password

    Options:
      -v,   Display current username
      -d,   Disable authentication

    Notes:
      - Credentials stored in /etc/system.conf
      - Applies to Telnet and FTP services
      - Empty password or -d disables security access
    """
    if len(args) == 0 or args[0]=="--h":
        print(doc)
        return
    
    elif len(args) == 3:
        
        if args[0].strip() == "":
            print("User name is not valid")
            return
        
        if args[1] != args[2]:
            print("Passwords are not the same")
            return
        
        sdata.sysconfig["auth"]["user"]  = args[0]
        sdata.sysconfig["auth"]["paswd"] = utls.sha1(args[1].strip())
        
        utls.save_conf_file(sdata.sysconfig, "/etc/system.conf")
        
        if args[1].strip() == "":
            print(f"Security has been disabled")
        else:
            print(f"New password has been set for user {args[0]}")
        
    elif len(args) == 1:
        if args[0] == "-v":
            print(f"Current user is {sdata.sysconfig['auth']['user']}")
            
        elif args[0] == "-d":
            sdata.sysconfig["auth"]["paswd"] = ""
            utls.save_conf_file(sdata.sysconfig, "/etc/system.conf")
            print(f"Security has been disabled")
            
        #TODO: Save file
    else:
        print(f"Invalid arguments")
            
        
