import sys
import utime
import utls
import sdata

# Process class
class Proc:
    
    def __init__(self):
        sdata._pid += 1               # Increment process Id
        self.pid   = sdata._pid       # Process id
        self.tid   = 0                # Thread id
        self.ext   = ""               # File extention / Call type
        self.cmd   = ""               # Command
        self.args  = ""               # Arguments
        self.stt   = utime.time()     # Start time
        self.sts   = "S"              # Process status
        self.rmmod = True             # Remove module ant end?, default True
        self.isthr = False
        
    def run(self, isthr, ext, cmd, args):
        self.isthr= isthr
        self.ext  = ext
        self.cmd  = cmd
        self.args = args

        try:

            sdata.procs.append(self)
            utls.setenv("#", self.pid)
            #print(f"{len(sdata.procs)=}")

            if self.isthr:
                utls.setenv("!", self.pid)
                from _thread import get_ident
                self.tid = get_ident()
                print(f"\n[{self.pid}]")
        
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
                        sdata.upyos.run_cmd("sh /bin/" + cmd + ".sh")
                    else:
                        sdata.upyos.run_cmd("sh " + cmd + ".sh")
                except Exception as e:
                    print(f"Error executing script {cmd}")
                    if sdata.debug:
                        sys.print_exception(e)
                
            else:
                print(f"{cmd}: Unknown function or program. Try 'help'.")

        except KeyboardInterrupt:
            print(f"{self.cmd}: ended")
        except ImportError as ie:
            self.rmmod=True
            print(f"{self.cmd}: Command not found\nor command import problem, try enable debug.")
            if sdata.debug:
                sys.print_exception(ie)
        except Exception as e:
            self.rmmod=True
            print(f"Error executing {self.cmd}")
            if sdata.debug:
                sys.print_exception(e)
        finally:

            # Check if multiple instances of a module are running
            for i in sdata.procs:
                if i.cmd == self.cmd and i.pid != self.pid:
                    self.rmmod=False # There is another modules instance running
                    break

            # Remove the module
            #print(f"{self.rmmod=}")
            if self.rmmod and self.cmd in sys.modules:
                del sys.modules[self.cmd]

            # Remove process from process list
            for idx, i in enumerate(sdata.procs):
                if i.pid == self.pid:
                    del sdata.procs[idx]
                    break
                
            # End of process
            if self.isthr:
                print(f"[{self.pid}]+ Done\t {self.cmd}{'.' + self.ext if self.ext else ''}")
