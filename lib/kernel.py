# Based in the work of Krzysztof Krystian Jankowski in http://smol.p1x.in/os/
# Developed by rbenrax 2023

import sys
import uos
import utime

import sdata
import utls

# Process class
class Proc:
    def __init__(self, syscall):
        
        self.syscall = syscall       # upyOS instance, for sytem calls
        
        sdata._pid += 1               # Increment process Id
        self.pid   = sdata._pid       # Process id
        self.tid   = 0                # Thread id
        self.ext   = ""               # File extention / Call type
        self.cmd   = ""               # Command
        self.args  = ""               # Arguments
        self.stt   = utime.ticks_ms() # Start time
        self.sts   = "S"              # Process status
        self.rmmod = True             # Remove module, default True
        self.isthr = False
        
    def run(self, isthr, ext, cmd, args):
        self.isthr= isthr
        self.ext  = ext
        self.cmd  = cmd
        self.args = args

        try:

            sdata.procs.append(self)
            #print(f"{len(sdata.procs)=}")

            if self.isthr:
                from _thread import get_ident
                self.tid = get_ident()
                print(f"\n[{self.pid}]")
                self.syscall.setenv("!", str(self.pid))
        
            # External Python commands and programs
            if ext=="py" or ext=="":
          
                mod = __import__(self.cmd)
                if '__main__' in dir(mod):

                    if hasattr(mod, 'proc'):      # Passing proc ref to run module
                        mod.proc=self

                    self.sts = "R"                # Process Running
                    
                    if len(self.args) > 0:
                        mod.__main__(self.args)
                    else:
                        mod.__main__("") # TODO: no nice

            # External shell scripts
            elif ext=="sh":
                
                try:
                    if not "/" in cmd:
                        self.syscall.run_cmd("sh /bin/" + cmd + ".sh")
                    else:
                        self.syscall.run_cmd("sh " + cmd + ".sh")
                except Exception as e:
                    print(f"Error executing script {cmd}")
                    if sdata.debug:
                        sys.print_exception(e)
                
            else:
                print(f"{cmd}: Unknown function or program. Try 'help'.")

        except KeyboardInterrupt:
            print(f"{self.cmd}: ended")
        except ImportError as ie:
            self.rmmod=False
            print(f"{self.cmd}: not found")
        except Exception as e:
            self.rmmod=False
            print(f"Error executing {self.cmd}")
            if sdata.debug:
                sys.print_exception(e)
        finally:

            # Check if several instances of module are running
            for i in sdata.procs:
                if i.cmd == self.cmd and i.pid != self.pid:
                    self.rmmod=False # There is another modules instance running
                    break

            #print(f"{self.rmmod=}")
            if self.rmmod and self.cmd in sys.modules:
                del sys.modules[self.cmd]

            # Remove process from process list
            for idx, i in enumerate(sdata.procs):
                if i.pid == self.pid:
                    del sdata.procs[idx]
                    break
                
            if self.isthr:
                print(f"[{self.pid}]+ Done\t {self.cmd}{'.' + self.ext if self.ext else ''}")

class upyOS:
    
    def __init__(self, boot_args):

        # Valid boot_args:
        # -r = Recovery mode
        # -n = No board config load

        # Remove modules previusly loaded by grub
        try:
            del sys.modules["syscfg"]
            del sys.modules["grub"]
        except:
            pass
        
        # sdata store all system data
        sdata.name    = "upyOS-" + uos.uname()[0]
        sdata.version = "0.5"
        sdata.initime = utime.time()

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
        sys.path.append("/extlib")

        # Clean screen and boot
        print("\033[2J\033[HBooting upyOS...")

        # Load system configuration and board definitions
        try:
            sdata.sysconfig=utls.load_conf_file("/etc/system.conf")
            #print(sdata.sysconfig)
            print("System cfg loaded.")
            
            if not "-n" in boot_args:
                sdata.board=utls.load_conf_file("/etc/" + sdata.name + ".board")
                #print(sdata.board)
                print("Board cfg loaded.")
            
        except OSError as ex:
            print("Problem loading configuration" + str(ex))
            if sdata.debug:
                sys.print_exception(ex)

        except Exception as ex:
            if sdata.debug:
                sys.print_exception(ex)
            pass

        # Internal Commands definition
        self.user_commands = {
            "ps": self.ps,
            "kill": self.kill,
            "killall": self.killall,
            #"getenv": self.getenv,
            #"setenv": self.setenv,
            #"unset": self.unset,
            "r": self.last_cmd,
            "exit" : self.exit
        }

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
        parts = fcmd.split()
        
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
                        newProc = Proc(self)
                        start_new_thread(newProc.run, (True, ext, cmdl, args[:-1]))
                    except ImportError:
                        print("System has not thread support")
                    except Exception as ex:
                        print(f"Error launching thread {ex}")

                        if sdata.debug:
                            sys.print_exception(ex)
                        
                else:
                    newProc = Proc(self)
                    newProc.run(False, ext, cmdl, args)

# - - -
           
    def getenv(self, var=""):
        """Get a value from environment variables"""
        #print(sysconfig["env"])
        for k, v in sdata.sysconfig["env"].items():
            if k == var:
                return v
        return("")

    def setenv(self, var="", val=""):
        """Set a value to a environment variable"""
        sdata.sysconfig["env"][var]=val

    def unset(self, var=""):
        """Remove a environment variable"""
        if sdata.sysconfig["env"][var]:
            del sdata.sysconfig["env"][var]

    def ps(self):
        """ Process status """
        if len(sdata.procs)>0:
            print(f"  Proc Sts     Init_T   Elapsed   Thread_Id   Cmd/Args")
            for i in sdata.procs:
                print(f"{i.pid:6}  {i.sts:3}  {i.stt:8}  {utime.ticks_ms() - i.stt:8}  {i.tid:10}   {i.cmd} {" ".join(i.args)}")
                
    def kill(self, pid="0"):
        """ Kill process """
        for i in sdata.procs:
            if pid.isdigit() and i.pid == int(pid):
                i.sts="S"
                break
            elif pid=="-a": #~ kill all process
                i.sts="S"
                
    def killall(self, pn=""):
        """ Kill process by name"""
        for i in sdata.procs:
            if pn in i.cmd:
                i.sts="S"

    # Repeat command
    def last_cmd(self):
        self.run_cmd(self.prev_cmd)

    # System exit
    def exit(self):

        if not sdata.debug:
            s=input("\nSalir S/[N] : ")
            if s.upper()!="S": return

        # Stop threads before exit
        if len(sdata.procs)>0:
            print("\nStoping process...")

            while len(sdata.procs)>0:
                print("Waiting...")
                utime.sleep(1)
                self.kill("-a")
                if len(sdata.procs)==1 and not sdata.procs[0].isthr: break

        self.print_msg("Shutdown upyOS..., bye.")
        print("")
        
        #raise SystemExit
        sys.exit()
        
    def print_msg(self, message):
        print(f"\n\033[1;37;44m->{message}\033[0m")

    def getboard(self):
        return sdata.board
    
    def getconf(self):
        return sdata.sysconfig

# - -  
if __name__ == "__main__":
    upyos = upyOS("-n") # Boot_args: -r -n
