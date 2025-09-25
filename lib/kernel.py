# Based in the work of Krzysztof Krystian Jankowski in http://smol.p1x.in/os/
# Developed by rbenrax 2023

import sys
import uos
import utime
from machine import reset as reboot

import sdata
import utls
import proc
import syscfg

class upyOS:

    # Valid boot_args:
    # -r = Recovery mode

    def __init__(self, boot_args):
        
        # Clean screen and boot
        print("\033[2J\033[HBooting upyOS...")
        
        # sdata store all system data
        sdata.name    = "upyOS-" + uos.uname()[0]
        sdata.version = "0.9"
        sdata.initime = utime.time()
        sdata.upyos   = self
        
        # Initialization

        board = uos.uname()[4]

        # Create directories
        if not utls.file_exists("/etc"):
            uos.mkdir("/etc")
            
        if not utls.file_exists("/opt"): # Specific solutions directory
            uos.mkdir("/opt")

        if not utls.file_exists("/tmp"): # Temp directory
            uos.mkdir("/tmp")

        # Set library path for modules finding, by default is /lib only
        sys.path.append("/bin")
        sys.path.append("/libx")

        # System ID
        from ubinascii import hexlify
        from machine import unique_id
        sdata.sid=hexlify(unique_id()).decode().upper()

        # Internal Commands definition
        self.user_commands = {
            "exit" : self.exit,
            #"halt": self.halt,
            "loadconfig": self.loadconfig,
            "loadboard": self.loadboard
        }

        sco=None # class with default configuration
        
        # Create sysconfig
        if not utls.file_exists("/etc/system.conf"):
            sco = syscfg.SysCfg(board) # create class with default structures
            utls.save_conf_file(sco.getConf(), "/etc/system.conf")
            print(f"/etc/system.conf file created.")

        self.loadconfig()

        if utls.file_exists("/etc/init.sh") and not "-r" in boot_args:
            self.print_msg("Normal mode boot")
            #print("Launching init.sh:")
            self.run_cmd("sh /etc/init.sh")

            if not sdata.board:
                file = "/etc/" + sdata.name + ".board"
                
                if not utls.file_exists(file):
                    if not sco:
                        sco = syscfg.SysCfg(board) # create class with default structures
                    utls.save_conf_file(sco.getBoard(), file)
                    print(f"\nBoard config file generated, you may config {file} before continue.")
                    
                    #self.loadboard(file)

        else:
            self.print_msg("Recovery mode boot")
            
        try:
            del sys.modules["syscfg"]
        except:
            pass

        self.print_msg("Type 'help' for a upyOS manual.")

        # Main command processing loop
        while True:
            try:
                user_input = input(uos.getcwd() + " $: ")
                self.run_cmd(user_input)
                
            except KeyboardInterrupt:
                self.exit()

            except EOFError:
                self.print_msg("Send EOF")

            except Exception as ex:
                print("cmd error, " + str(ex))
                if sdata.debug:
                    sys.print_exception(ex)
                pass
 
 # - - - - - - - -

    def run_py_code(self, code):
        exec(code.replace('\\n', '\n'))

    #@utls.timed_function
    def run_cmd(self, fcmd):

        fcmd=fcmd.strip()
        
        # Translate env variables $*
        tmp = fcmd.split()
 
        for e in tmp:
            if e[0]=="$":
                #v=utls.getenv(e[1:])
                #fcmd = fcmd.replace(e, v)
                fcmd = fcmd.replace(e, '"' + str(utls.getenv(e[1:])) + '"' )
        if fcmd[:2]=="> ":
            self.run_py_code(fcmd[2:])
            return
        elif fcmd[:2]=="< ":
            self.run_py_code(f"print({fcmd[2:]})")
            return
        elif fcmd[:2]=="./":
            cwd = uos.getcwd()
            if cwd == "/":
                fcmd = "/" + fcmd[2:]
            else:
                fcmd = cwd + "/" + fcmd[2:]

        # Separate full command elements
        #parts = fcmd.split()
        parts = utls.shlex(fcmd)
        
        if len(parts) > 0:

            # Get command 
            cmd = parts[0]
            
            args=[]
            
            # Get command arguments
            if len(parts) > 1:
                args = parts[1:]
                #print(f"{args=} ")
            
            # Internal commands
            if cmd in self.user_commands:
                if len(args) > 0:
                    self.user_commands[cmd](*args)
                else:
                    self.user_commands[cmd]()

            # External commands or scripts
            else:
                tmp = cmd.split(".")
                if len(tmp) > 1:
                    cmdl = tmp[0]
                    ext  = tmp[-1]
                else:
                    cmdl = cmd
                    ext  = ""

                if len(parts) > 1 and parts[-1]=="&": # If new thread
                    # RP-2040 suport only two threads, esp32 and others, many
                    try:
                        from _thread import start_new_thread, stack_size
                        #if uos.uname()[0]=="esp32": stack_size(7168)   # stack overflow in ESP32C3
                        if sys.platform=="esp32": stack_size(8192)   # stack overflow in ESP32C3
                        newProc = proc.Proc(self)
                        start_new_thread(newProc.run, (True, ext, cmdl, args[:-1]))
                        utime.sleep(.150)
                    except ImportError:
                        print("System has not thread support")
                    except Exception as ex:
                        print(f"Error launching thread {ex}")

                        if sdata.debug:
                            sys.print_exception(ex)
                        
                else:
                    newProc = proc.Proc(self)
                    newProc.run(False, ext, cmdl, args)

# - - -
                
    def killall(self, pn=""):
        for i in sdata.procs:
            if pn in i.cmd:
                i.sts="S"

    # System exit
    def exit(self, mod=""):

        if not sdata.debug:
            while True:
                try:
                    if "utelnetserver" in sys.modules:
                        print("Telnet is active, stop it, or use reset instead")
                        return            
                
                    s=input("\nExit upyOS Y/[N] : ")
                    if s.upper()!="Y":
                        return
                    else:
                        break
                except KeyboardInterrupt:
                    pass

        try:
            # Stop threads before exit
            if len(sdata.procs)>0:
                print("\nStoping process...")

                # Launch shutdown services script
                if utls.file_exists("/etc/end.sh"):
                    self.run_cmd("sh /etc/end.sh")

                self.killall("")
                while True:
                    end=True
                    for p in sdata.procs:
                        if p.isthr: end=False
                    if end: break
                    utime.sleep(.5)
                    
            self.print_msg("Shutdown upyOS..., bye.")
            print("")
            
            if mod=="-r":
                reboot()
            else:
                raise SystemExit
                #sys.exit()
                
        except KeyboardInterrupt:
            pass

    def print_msg(self, message):
        print(f"\n\033[1;37;44m->{message}\033[0m")
        # Load system configuration and board definitions
     
    def loadconfig(self, conf="/etc/system.conf"):
        if utls.file_exists(conf):
            sdata.sysconfig=utls.load_conf_file(conf)
            print(f"System cfg loaded: {conf}")
        else:
            print(f"{conf} not found")
        
    def loadboard(self, board=""):
        if board == "": board = "/etc/" + sdata.name + ".board"
        if utls.file_exists(board):
            sdata.board=utls.load_conf_file(board)
            print(f"Board cfg loaded: {board}")
        else:
            print(f"{board} not found")

# - -  
if __name__ == "__main__":
    upyos = upyOS("-n") # Boot_args: -r
