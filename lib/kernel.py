# Based in the work of Krzysztof Krystian Jankowski in http://smol.p1x.in/os/
# Developed by rbenrax 2023

import sys
import uos
import utime

import sdata
import utls
import proc

class upyOS:
    
    def __init__(self, boot_args):
        
        # Valid boot_args:
        # -r = Recovery mode
        
        # sdata store all system data
        sdata.name    = "upyOS-" + uos.uname()[0]
        sdata.version = "0.6"
        sdata.initime = utime.time()

        # Remove modules previusly loaded by grub
        try:
            del sys.modules["syscfg"]
            del sys.modules["grub"]
        except:
            pass

        # System ID
        from ubinascii import hexlify
        from machine import unique_id
        sdata.sid=hexlify(unique_id()).decode()
        
        # Create directories
        if not utls.file_exists("/opt"): # Specific solutions directory
            uos.mkdir("/opt")

        if not utls.file_exists("/tmp"): # Temp directory
            uos.mkdir("/tmp")

        # Set library path for modules finding, by default is /lib only
        sys.path.append("/bin")
        sys.path.append("/libx")

        # Internal Commands definition
        self.user_commands = {
            #"ps": self.ps,
            #"kill": self.kill,
            #"killall": self.killall,
            "exit" : self.exit,
            #"halt": self.halt,
            "loadconfig": self.loadconfig,
            "loadboard": self.loadboard,
            "r": self.last_cmd
            
        }

        # Clean screen and boot
        print("\033[2J\033[HBooting upyOS...")

        self.loadconfig()

        if not "env" in sdata.sysconfig:
            sdata.sysconfig={"ver"     : 1.0,
                           "aliases" : {"": ""},
                           "pfiles"  : ["/boot.py","/main.py"],
                           "env"     : {"TZ": "+2", "?": "", "0": ""}
                           }

        #self.loadboard() # Called from /etc/init.sh

        if utls.file_exists("/etc/init.sh") and not "-r" in boot_args:
            self.print_msg("Normal mode boot")
            
            #print("Launching init.sh:")
            self.run_cmd("sh /etc/init.sh")

            #/etc/rc.local
            print("Launching rc.local:")
            self.run_cmd("sh /etc/rc.local")
        else:
            self.print_msg("Recovery mode boot")
        
        self.prev_cmd=""
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
                v=utls.getenv(e[1:])
                fcmd = fcmd.replace(e, v)

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
            
            # Translate command aliases
            if sdata.sysconfig:
                if cmd in sdata.sysconfig["aliases"]:    
                    cmd=sdata.sysconfig["aliases"][cmd]
            
            # Last command repeat 
            if cmd!="r":
                self.prev_cmd = fcmd
            
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
           
#    def getenv(self, var=""):
#        return utls.getenv(var)

#    def setenv(self, var="", val=""):
#        utls.setenv(var, val)
 
#    def unset(self, var=""):
#        utls.unset(var)

#    def ps(self):
#        if len(sdata.procs)>0:
#            print(f"  Proc Sts     Init_T   Elapsed   Thread_Id   Cmd/Args")
#            for i in sdata.procs:
#                print(f"{i.pid:6}  {i.sts:3}  {i.stt:8}  {utime.ticks_ms() - i.stt:8}  {i.tid:10}   {i.cmd} {" ".join(i.args)}")
                
#    def kill(self, pid="0"):
#        for i in sdata.procs:
#            if pid.isdigit() and i.pid == int(pid):
#                i.sts="S"
#                break
                
    def killall(self, pn=""):
        for i in sdata.procs:
            if pn in i.cmd:
                i.sts="S"

    # Repeat command
    def last_cmd(self):
        self.run_cmd(self.prev_cmd)

    # System exit
    def exit(self):

        if not sdata.debug:
            s=input("\nExit upyOS S/[N] : ")
            if s.upper()!="S": return

        # Stop threads before exit
        if len(sdata.procs)>0:
            print("\nStoping process...")
            
            self.killall("")
            while True:
                end=True
                for p in sdata.procs:
                    if p.isthr: end=False
                if end: break
                utime.sleep(.5)
                
        # Launch shutdown script
        if utls.file_exists("/etc/down.sh"):
            self.run_cmd("sh /etc/down.sh")

        self.print_msg("Shutdown upyOS..., bye.")
        print("")
        
        #raise SystemExit
        sys.exit()
        
    def print_msg(self, message):
        print(f"\n\033[1;37;44m->{message}\033[0m")
        # Load system configuration and board definitions
     
#    def halt(self):
#        sys.exit()
     
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

#    def getconf(self):
#        return sdata.sysconfig

#    def getboard(self):
#        return sdata.board

# - -  
if __name__ == "__main__":
    upyos = upyOS("-n") # Boot_args: -r
