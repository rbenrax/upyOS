# smolOS by Krzysztof Krystian Jankowski
# Homepage: http://smol.p1x.in/os/
# Adptated by rbenrax

import sys
import sdata
import uos
import utls

class smolOS:
    def __init__(self):

        try:
            del sys.modules["syscfg"]
            del sys.modules["grub"]
        except:
            pass
        
        sdata.name    = "smolOS-" + uos.uname()[0]
        sdata.version = "0.5 rbenrax"

        if not utls.file_exists("/opt"): # Specific solutions directory
            uos.mkdir("/opt")

        if not utls.file_exists("/tmp"): # Temp directory
            uos.mkdir("/tmp")

        sys.path.append("/bin")
        sys.path.append("/extlib")

        self.clear()
        print("Booting smolOS...")

        # Load system  configuration and board definitions
        try:
            sdata.sysconfig=utls.load_conf_file("/etc/system.conf")
            #print(sdata.sysconfig)
            print("System cfg loaded.")
            
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

        # Internal Commands def
        self.user_commands = {
            "help": self.help,
            "clear": self.clear,
            "cp" : self.cp,
            "mv" : self.mv,
            "rm": self.rm,
            "pwd": self.pwd,
            "cd": self.chdir,
            "mkdir": self.mkdir,
            "rmdir": self.rmdir,
            "sh" : self.run_sh_script,
            "py": self.run_py_code,
            "r": self.last_cmd,
            "exit" : self.exit
        }

        self.boot()

    def boot(self):

        if "turbo" in sdata.sysconfig:
            if sdata.sysconfig["turbo"]:
                self.run_cmd("cpufreq -turbo")
            else:
                self.run_cmd("cpufreq -low")
            
        if utls.file_exists("/etc/init.sh"):
            self.print_msg("Normal mode boot")
            
            #/etc/init.sh
            #print("Launching init.sh:")
            self.run_cmd("sh /etc/init.sh")

            #/etc/rc.local
            print("Launching rc.local:")
            self.run_cmd("sh /etc/rc.local")
        else:
            self.print_msg("Recovery mode boot")
        
        self.prev_cmd=""
        self.print_msg("Type 'help' for a smolOS manual.")

        # Main Loop
        while True:
            try:
                user_input = input(uos.getcwd() + " $: ")
                self.run_cmd(user_input)
                
            except KeyboardInterrupt:
                self.print_msg("Shutdown smolOS..., bye.")
                sys.exit()

            except EOFError:
                self.print_msg("Send EOF")

            except Exception as ex:
                self.print_err("cmd error, " + str(ex))
                if sdata.debug:
                    sys.print_exception(ex)
                pass
 
 # - - - - - - - -
 
    def run_cmd(self, fcmd):

        fcmd=fcmd.strip()

        if fcmd[:3]=="py ":
            #print(f"{fcmd}")
            self.run_py_code(fcmd[3:])
            return

        parts = fcmd.split()
        
        if len(parts) > 0:
            cmd = parts[0]
            
            if cmd!="r":
                self.prev_cmd = fcmd
            
            #print(f"{cmd=}")
            args=[]
            
            if len(parts) > 1:
                args = parts[1:]
                #print(f"{args=} ")
            
            if sdata.sysconfig:
                if cmd in sdata.sysconfig["aliases"]:    # aliases support
                    cmd=sdata.sysconfig["aliases"][cmd]
            
            if cmd in self.user_commands:
                if len(args) > 0:
                    self.user_commands[cmd](*args)
                else:
                    self.user_commands[cmd]()
            else:
                tmp = cmd.split(".")
                if len(tmp) > 1:
                    cmdl = tmp[0]
                    ext  = tmp[-1]
                else:
                    cmdl = cmd
                    ext  = ""

                if ext=="py" or ext=="":
                    imerr=False
                    try:
                        ins = __import__(cmdl)
                        if '__main__' in dir(ins):
                            if len(args) > 0:
                                ins.__main__(args)
                            else:
                                ins.__main__("")

                    except KeyboardInterrupt:
                        print(f"{cmd}: ended")
                    except ImportError as ie:
                        imerr=True
                        print(f"{cmd}: not found")
                    except Exception as e:
                        imerr=True
                        print(f"Error executing {cmd}")
                        sys.print_exception(e)
                    
                    finally:
                        if not imerr:
                            del sys.modules[cmdl]

                elif ext=="sh":
                    try:
                        if not "/" in cmdl:
                            self.run_sh_script("/bin/" + cmdl + ".sh")
                        else:
                            self.run_sh_script(cmdl + ".sh")
                    except Exception as e:
                        print(f"Error executing script {command}")
                        sys.print_exception(e)
                    
                else:
                    self.print_err("Unknown function or program. Try 'help'.")

    def last_cmd(self):
        # Only runs in full terminals where is unnecesary
        #from editstr import editstr
        #print('┌───┬───┬───┬───┬───┬───')
        #cmd = editstr(self.prev_cmd)
        #self.run_cmd(cmd)
        #del sys.modules["editstr"]
        self.run_cmd(self.prev_cmd)

    def run_sh_script(self, ssf):
        if utls.file_exists(ssf):
            with open(ssf,'r') as f:
                while True:
                    lin = f.readline()
                    if not lin: break

                    if lin.strip()=="": continue
                    if len(lin)>0 and lin[0]=="#": continue
                    cmdl=lin.split("#")[0] # Left comment line part
                    
                    # Translate env variables $*
                    tmp = cmdl.split()
                    
                    if not tmp[0] in ["export", "echo", "unset"]:
                        for e in tmp:
                            if e[0]=="$":
                                v=sdata.getenv(e[1:])
                                cmdl = cmdl.replace(e, v)

                    self.run_cmd(cmdl)
        else:
            print(f"{ssf}: script not found")
 
    def run_py_code(self, code):
        exec(code.replace('\\n', '\n'))

# - - -

    def help(self):
        print(sdata.name + " version: " + sdata.version + "\n")

        self.run_cmd("cat /etc/help.txt")
        
        print("External commands:\n")
        
        tmp=uos.listdir("/bin")
        tmp.sort()
        buf=""
        for ecmd in tmp:
            if ecmd.endswith(".py"):
                buf += ecmd[:-3] + ", "
            else:
                buf += ecmd + ", "
        
        print(buf[:-2])

    def clear(self):
         print("\033[2J")
         print("\033[H")

    def exit(self):
        raise SystemExit

    def print_err(self, error):
        print(f"\n\033[1;37;41m<!>{error}<!>\033[0m")

    def print_msg(self, message):
        print(f"\n\033[1;34;47m->{message}\033[0m")
            
# - -  
 
    def cp(self, spath="", dpath=""):
        if spath == "" or dpath=="": return
        if not utls.file_exists(spath):
            self.print_err("File source not exists.")
            return
        
        sfile = spath.split("/")[-1]
        try:
            uos.listdir(dpath)
            dpath += "/" + sfile
        except OSError:
            pass  
        
        if utls.protected(dpath):
            self.print_err("Can not overwrite system file!")
        else:                  
            with open(spath, 'rb') as fs:
                with open(dpath, "wb") as fd:
                    while True:
                        buf = fs.read(256)
                        if not buf:
                            break
                        fd.write(buf)

    def mv(self,spath="", dpath=""):
        if spath == "" or dpath == "": return

        if not utls.file_exists(spath):
            self.print_err("File source not exists.")
            return

        sfile = spath.split("/")[-1]
        try:
            uos.listdir(dpath)
            dpath += "/" + sfile
        except OSError:
            pass

        if utls.protected(spath):
            self.print_err("Can not move system files!")
        else:
            uos.rename(spath, dpath)

    def rm(self, filename=""):
        if filename == "": return
        if utls.protected(filename):
            self.print_err("Can not remove system file!")
        else:
            uos.remove(filename)

    def pwd(self):
        print(uos.getcwd())
       
    def mkdir(self, path=""):
        try:
            uos.mkdir(path)
        except OSError:
            print("Invalid path")
            
    def rmdir(self, path=""):
        try:
            uos.rmdir(path)
        except OSError:
            print("Invalid path")
            
    def chdir(self, path=""):
        try:
            uos.chdir(path)
        except OSError:
            print("Invalid path")

# Module test
if __name__ == "__main__":
    smol = smolOS()
