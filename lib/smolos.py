# smolOS by Krzysztof Krystian Jankowski
# Homepage: http://smol.p1x.in/os/

# Mods by rbenrax

import sdata
import utls
from machine import freq
import uos
import utime
import sys

class smolOS:
    def __init__(self):

        try:
            del sys.modules["syscfg"]
            del sys.modules["grub"]
            #print(sys.modules)
        except:
            pass
        
        sys.path.append("/bin")
        sys.path.append("/extlib")
        
        sdata.name    = "smolOS-" + uos.uname()[0]
        sdata.version = "0.3 rbenrax"
        
        # Load board config
        try:
            sdata.board=utls.load_conf_file("/etc/" + sdata.name + ".board")
            self.cpu_speed_range = sdata.board["mcu"][0]["speed"] # speed of cpu 0

            #print(sdata.board)
            #...
            print("Board config loaded.")
            
            sdata.sysconfig=utls.load_conf_file("/etc/system.conf")
            self.turbo = sdata.sysconfig["turbo"]
            self.user_commands_aliases = sdata.sysconfig["aliases"]
            self.protected_files = sdata.sysconfig["pfiles"]
            #...
            print("System config loaded.")
            
        except OSError as ex:
            self.cpu_speed_range = {"slow":80,"turbo":160} # Mhz

            self.turbo = False
            self.user_commands_aliases = {"h": "help"}
            self.protected_files = ["boot.py","main.py"]
            
            print("Problem loading board config. " + str(ex))
            
            if sdata.debug:
                sys.print_exception(ex)

        except Exception as ex:
            #print(ex)
            if sdata.debug:
                sys.print_exception(ex)
            pass

        #self.thread_running = False

        self.user_commands = {
            "help": self.help,
            "man" : self.man,
            "ls": self.ls,
            "cat": self.cat,
            "cp" : self.cp,
            "mv" : self.mv,
            "rm": self.rm,
            "clear": self.cls,
            "turbo": self.toggle_turbo,
            "info": self.info,
            "run": self.run,
            "sh" : self.sh,
            "exe": self.exe,
            "pwd": self.pwd,
            "mkdir": self.mkdir,
            "rmdir": self.rmdir,
            "cd": self.chdir,
            "exit" : self.exit
            
        }
        self.user_commands_manual = {
            "help": "This help",
            "man" : "Single command help",
            "ls": "List files",
            "cat": "print filename content",
            "cp": "cp <file source> <file destination>, copy a single file",
            "mv": "mv <file source> <file destination>, move o rename a single file",
            "rm": "rm <file>, remove a file (be careful!)",
            "clear": "clears the screen",
            "turbo": "toggles turbo mode (100% vs 50% CPU speed)",
            "info": "information about a file",
            "run": "runs external python program",
            #"sh" : "run external sh script",
            "exe": "Running exec(code)",
            "pwd": "Show current directory",
            "mkdir": "Make directory",
            "rmdir": "Remove directory",
            "cd": "Change default directory",
            "exit" : "Exit to Micropython shell"
        }

        self.boot()

    def boot(self):

        if self.turbo:
            freq(self.cpu_speed_range["turbo"] * 1000000)
        else:
            freq(self.cpu_speed_range["slow"] * 1000000)
            
        ##TODO: Load modules
            
        ## End modules

        self.cls()
        self.welcome()

        #/etc/rc.local
        print("\n\033[0mLaunching rc.local commands:\n")
        self.run_sh_script("/etc/rc.local")
        
        self.print_msg("Type 'help' for a smol manual.")

        while True:
            try:
                user_input = input("\n" + uos.getcwd() + " $: ")
                self.run_cmd(user_input)
            except KeyboardInterrupt:
                 self.print_msg("Shutdown smolOS..., bye.")
                 sys.exit()
      
            except Exception as ex:
                self.print_err("cmd error, " + str(ex))
                if sdata.debug:
                    sys.print_exception(ex)
                pass
 
 # - - - - - - - -
 
    def run_cmd(self, cmd):
        parts = cmd.split()
        if len(parts) > 0:
            command = parts[0]
            
            if command in self.user_commands_aliases: # aliases support
                command=self.user_commands_aliases[command]
            
            if command in self.user_commands:
                if len(parts) > 1:
                    arguments = parts[1:]
                    self.user_commands[command](*arguments)
                else:
                    self.user_commands[command]()
            else:
                tmp = command.split(".")
                if len(tmp) == 2:
                    cmd = tmp[0]
                    ext = tmp[1]
                else:
                    cmd = command
                    ext = ""

                #print(line)
                
                if utls.file_exists("/bin/" + cmd + ".py"):
                    
                    try:
                        ins = __import__(cmd)
                        if '__main__' in dir(ins):
                            if len(parts) > 1:
                                args = parts[1:]
                                ins.__main__(args)
                            else:
                                ins.__main__("")

                    except Exception as e:
                        print(f"Error executing script {command}")
                        sys.print_exception(e)
                    
                    finally:
                        del sys.modules[cmd]

                elif ext=="sh":
                    
                    try:
                        self.run_sh_script("/bin/" + cmd + ".sh")
                    except Exception as e:
                        print(f"Error executing script {command}")
                        sys.print_exception(e)
                    
                else:
                    self.unknown_function()

    def run_sh_script(self, ssf):
        if utls.file_exists(ssf):
            with open(ssf,'r') as f:
                cont = f.read()
                for lin in cont.split("\n"):
                    if len(lin)>1 and lin[0]=="#": continue
                    cmd=lin.split("#")
                    self.run_cmd(cmd[0])
 
    def run(self, fn=""):
        if fn == "":
            self.print_err("Specify a file name to run.")
            return
        
        if utls.file_exists(fn):
            exec(open(fn).read())
        else:
            self.print_err(f"{fn} does not exists.")

    def sh(self, shsf):
        self.run_sh_script(shsf)

    def exe(self,command):
        exec(command)
        
    def exit(self):
        raise SystemExit
 
    def toggle_turbo(self):
        self.turbo = not self.turbo
        if self.turbo:
            f = self.cpu_speed_range["turbo"]
        else:
            f = self.cpu_speed_range["slow"]
        freq(f * 1000000)
        self.print_msg("CPU speed set to "+str(f)+" Mhz")

    def cls(self):
         print("\033[2J")
         print("\033[H")
 
 # - - -
 
    def banner(self):
        print("\033[1;33;44m                                 ______  _____")
        print("           _________ ___  ____  / / __ \/ ___/")
        print("          / ___/ __ `__ \/ __ \/ / / / /\__ \ ")
        print("         (__  ) / / / / / /_/ / / /_/ /___/ / ")
        print("        /____/_/ /_/ /_/\____/_/\____//____/  ")
        print("-------------\033[1;5;7mTINY-OS-FOR-TINY-COMPUTERS\033[0;1;33;44m------------\n\033[0m")

    def welcome(self):
        self.banner()
        self.run_cmd("lshw.py -b")
        
        print("\n\033[1mMemory:")
        self.run_cmd("free")
        print("\n\033[1mStorage:")
        self.run_cmd("df")

    def man(self,cmd=""):
        try:
            desc = self.user_commands_manual[cmd]
            print(f"\033[1m{cmd}\033[0m - {desc}")
        except:
            self.print_err("Man not available for command " + cmd)

    def help(self):
        print(sdata.name + " version " + sdata.version + " user commands:\n")

        # Ordering
        ok = list(self.user_commands_manual.keys())
        ok.sort()
        
        for k in ok:
            print(f"\033[1m{k}\033[0m -{self.user_commands_manual[k]}")
        
        print("\n\033[0;32mSystem created by Krzysztof Krystian Jankowski, Mods by rbenrax.")
        print("Source code available at \033[4msmol.p1x.in/os/")
        print("Source code available at \033[4https://github.com/rbenrax/smolOS\033[0m")

    def print_err(self, error):
        print(f"\n\033[1;37;41m<!>{error}<!>\033[0m")
        utime.sleep(1)

    def print_msg(self, message):
        print(f"\n\033[1;34;47m->{message}\033[0m")
        utime.sleep(0.5)

    def unknown_function(self):
        self.print_err("unknown function. Try 'help'.")

# - - 

    def ls(self, mode="-l"):
        tsize=0
        
        tmp=uos.listdir()
        tmp.sort()
        for file in tmp:
            tsize += self.info(file, mode)

        if 'h' in mode:
            print(f"\nTotal: {utls.human(tsize)}")
        else:
            print(f"\nTotal: {tsize} bytes")
            
    def info(self, filename="", mode="-a"):
        if not utls.file_exists(filename):
            self.print_err("File not found")
            return
        
        # Hiden file
        if mode!="-a":
            if filename[1]==".": return 0
        
        stat = utls.get_stat(filename)
        
        #mode = stat[0]
        size = stat[6]
        mtime = stat[8]
        localtime = utime.localtime(mtime)

        if utls.isdir(filename):
            fattr= "d"
        else:
            fattr= " "

        if filename in self.protected_files:
            fattr += "r-"
        else:
            fattr += "rw"

        if ".py" in filename:
            fattr += 'x'
        else:
            fattr += '-'
        
        if "h" in mode:
            ssize = f"{utls.human(size)}"
        else:
            ssize = f"{size:7}"
            
        print(f"{fattr} {ssize} {utls.MONTH[localtime[1]]} " + \
              f"{localtime[2]:0>2} {localtime[4]:0>2} {localtime[5]:0>2} {filename}")
              
        return size

    def cat(self,filename=""):
        if filename == "":
            self.print_err("Failed to open the file.")
            return
        with open(filename,'r') as file:
            content = file.read()
            print(content)

    def cp(self, fns="", fnd=""):
        if fns == "" or fnd=="":
            self.print_err("Invalid file(s). Failed to copy the file.")
            return
        if not utls.file_exists(fns):
            self.print_err("File source not exists.")
            return            
        if fnd in self.protected_files:
            self.print_err("Can not overwrite system file!")
        else:
            with open(fns, 'rb') as fs:
                with open(fnd, "wb") as fd:
                    while True:
                        buf = fs.read(256)
                        if not buf:
                            break
                        fd.write(buf)
            
            self.print_msg("File copied successfully.")

    def mv(self,spath="", dpath=""):
        if spath == "" or dpath == "":
            self.print_err("Invalid file(s). Failed to move the file.")
            return
        if spath in self.protected_files:
            self.print_err("Can not move system file!")
        else:
            uos.rename(spath, dpath)
            self.print_msg("File moved successfully.")

    def rm(self,filename=""):
        if filename == "":
            self.print_err("Failed to remove the file.")
            return
        if filename in self.protected_files:
            self.print_err("Can not remove system file!")
        else:
            uos.remove(filename)
            self.print_msg(f"File {filename} removed successfully.")

    def pwd(self):
        print(uos.getcwd())
       
    def mkdir(self, path=""):
        uos.mkdir(path)
    
    def rmdir(self, path=""):
        uos.rmdir(path)
        
    def chdir(self, path=""):
        uos.chdir(path)

smol = smolOS()

