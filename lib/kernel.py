# Based in the work of Krzysztof Krystian Jankowski in http://smol.p1x.in/os/
# Developed by rbenrax 2023

import sys
import uos
import utime

import sdata
import utls

_pid=0
procs=[]

# Process class
class Proc:
    def __init__(self, syscall):
        
        self.syscall = syscall       # upyOS instance, for sytem calls
        
        global _pid
        _pid += 1
        self.pid   = _pid             # Process id
        self.tid   = 0                # Thread id
        self.cmd   = ""               # Command
        self.args  = ""               # Arguments
        self.stt   = utime.ticks_ms() # Start time
        self.sts   = "S"              # Process status
        self.rmmod = True             # Remove module, default True
        self.isthr = False
        
    def run(self, isthr, cmd, args):
        self.isthr= isthr
        self.cmd  = cmd
        self.args = args
        
        global procs
        procs.append(self)

        if self.isthr:
            from _thread import get_ident
            self.tid = get_ident()
            print(f"\n[{self.pid}]")
        
        try:
            mod = __import__(self.cmd)
            if '__main__' in dir(mod):

                if hasattr(mod, 'proc'):      # Passing proc ref to run module
                    mod.proc=self

                self.sts = "R"                # Process Running
                
                if len(self.args) > 0:
                    mod.__main__(self.args)
                else:
                    mod.__main__("") # TODO: no nice

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
            for i in procs:
                if i.cmd == self.cmd and i.pid != self.pid:
                    self.rmmod=False # There is another modules instance running
                    break

            #print(f"{self.rmmod=}")
            if self.rmmod:
                del sys.modules[self.cmd]

            # Remove process from process list
            for idx, i in enumerate(procs):
                if i.pid == self.pid:
                    del procs[idx]
                    break
                
            if self.isthr:
                print(f"[{self.pid}]+ Done\t {self.cmd}")

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
            "r": self.last_cmd,
            "getenv": self.getenv,
            "setenv": self.setenv,
            "unset": self.unset,
            "exit" : self.exit
        }

        if "turbo" in sdata.sysconfig:
            if sdata.sysconfig["turbo"]:
                self.run_cmd("cpufreq -turbo")
            else:
                self.run_cmd("cpufreq -low")

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

                # External Python commands and programs
                if ext=="py" or ext=="":

                    if len(parts) > 1 and parts[-1]=="&": # If new thread
                        # Since most microcontrollers only have one thread more...
                        # One main thread an alternative one, for now
                        try:
                            from _thread import start_new_thread, stack_size
                            if uos.uname()[0]=="esp32": stack_size(7168)   # stack overflow in ESP32C3
                            newProc = Proc(self)
                            start_new_thread(newProc.run, (True, cmdl, args[:-1]))
                        except ImportError:
                            print("System has not thread support")
                        except Exception as ex:
                            print(f"Error launching thread {ex}")

                            if sdata.debug:
                                sys.print_exception(ex)
                            
                    else:
                        newProc = Proc(self)
                        newProc.run(False, cmdl, args)

                # External shell scripts
                elif ext=="sh":
                    try:
                        if not "/" in cmdl:
                            self.run_cmd("sh /bin/" + cmdl + ".sh")
                        else:
                            self.run_cmd("sh " + cmdl + ".sh")
                    except Exception as e:
                        print(f"Error executing script {fcmd}")
                        sys.print_exception(e)
                    
                else:
                    print(f"{cmd}: Unknown function or program. Try 'help'.")

# - - -

    # Repeat command
    def last_cmd(self):
        # Only runs in full terminals where is unnecesary
        #from editstr import editstr
        #print('┌───┬───┬───┬───┬───┬───')
        #cmd = editstr(self.prev_cmd)
        #self.run_cmd(cmd)
        #del sys.modules["editstr"]
        self.run_cmd(self.prev_cmd)
            
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

    # System exit
    def exit(self):

        # Stop threads before exit
        if len(procs)>0:
            print("\nStoping process...")
            for i in procs:
                i.sts="S"   #self.run_cmd(f"kill {i.pid}")

            #TODO: solve if sh script send exit command
            while len(procs)>0:
                print("\nWaiting...")
                utime.sleep(1)

        self.print_msg("Shutdown upyOS..., bye.")
        print("")
        
        raise SystemExit
        #sys.exit()

    def print_msg(self, message):
        print(f"\n\033[1;34;47m->{message}\033[0m")

# - -  
if __name__ == "__main__":
    upyos = upyOS("") # Boot_args: -r -n
