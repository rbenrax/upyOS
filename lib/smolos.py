# smolOS by Krzysztof Krystian Jankowski
# Homepage: http://smol.p1x.in/os/

# Mods by rbenrax

import machine
import uos
import gc
import utime
import sys
import json
import utls

class smolOS:
    def __init__(self):
        self.board = uos.uname()[4]
        self.name = "smolOS-" + uos.uname()[0]
        self.version = "0.2 rbenrax"
           
        # Serializable ->
        #self.system_leds_pins=[12, 13]
        #self.cpu_speed_range = {"slow":80,"turbo":80} # Mhz
        #self.turbo = False

        #self.user_commands_aliases = {
        #    "h": "help",
        #    "list": "ls",
        #    "show": "cat",
        #    "remove": "rm",
        #    "edit": "vi"         
        #}
        # <- 
        
        # Load board config
        try:
            with open("/etc/" + self.name + ".board", "r") as bcf:
                bc=utls.load(bcf)

                self.cpu_speed_range = bc["mcu"]["speed"] # Mhz
                #print(self.cpu_speed_range)
                
                self.system_leds_pins=bc["ledio"][0].values()
                #print(self.system_leds_pins)
                
                self.rgb_led_pins=bc["rgbio"][0].values()
                #print(self.rgb_led_pins)
                #...

            with open("/etc/system.conf", "r") as scf:
                sc=utls.load(scf)

                self.turbo = sc["turbo"]
                #print(self.turbo)
                
                self.user_commands_aliases = sc["aliases"]
                #print(self.user_commands_aliases)
                #...
                
            print("Board config loaded.")
        except OSError as ex:
            print("Problem loading board config. " + str(ex))
            
        #except Exception as ex:
        #    print(ex)
        #pass

        #self.thread_running = False
        self.protected_files = ["boot.py","main.py", "grub.py"]

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
            "vi": self.ed,
            "info": self.info,
            "py": self.py,
            "led": self.led,
            "exe": self.exe,
            "pwd": self.pwd,
            "mkdir": self.mkdir,
            "rmdir": self.rmdir,
            "cd": self.chdir,
            "touch": self.touch,
            "free" : self.free,
            "df" : self.df,
            "lshw" : self.lshw,
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
            "vi": "text editor, filename is optional",
            "info": "information about a file",
            "py": "runs user program",
            "led": "led <command> <led number>, manipulating on-board LED. Commands: `on`, `off`, Led number: [0,1,...]",
            "exe": "Running exec(code)",
            "pwd": "Show current directory",
            "mkdir": "Make directory",
            "rmdir": "Remove directory",
            "cd": "Change default directory",
            "touch": "touch <filename> <line content1> <line content2> <line content3>, Create or add a line to a file with three fields",
            "free" : "Show ram status",
            "df" : "Show storage status",
            "lshw" : "Show hardware",
            "exit" : "Exit to Micropython shell"
        }
        self.ed_commands_manual = {
            "help": "this help",
            ">": "next page",
            "<": "previous page",
            "10 <line of text>": "replacing 10-th line with a line of text",
            "append <lines>": "append new line(s) at the end of a file, default 1",
            "write or save": "write changes to a file (not implemented yet)",
            "quit": "quit"
        }

        self.boot()

    def boot(self):
        if self.turbo:
            machine.freq(self.cpu_speed_range["turbo"] * 1000000)

        #TODO: Load modules
        self.system_leds = []
        for ln in self.system_leds_pins: #Leds Pins
            self.system_leds.append(machine.Pin(ln,machine.Pin.OUT))
            
        ## Endd modules

        self.cls()
        self.welcome()

        self.led("boot", 0)
        #self.led("rgb", 1)
        
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
                 
      #      except Exception as ex:
      #          self.print_err("cmd error, " + str(ex))
      #          pass
 
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
                self.unknown_function()
 
    def run_sh_script(self, ssf):
        if utls.file_exists(ssf):
            with open(ssf,'r') as f:
                cont = f.read()
                for cmd in cont.split("\n"):
                    if len(cmd)>1 and cmd[0]=="#": continue
                    self.run_cmd(cmd)
 
    def banner(self):
        print("\033[1;33;44m                                 ______  _____")
        print("           _________ ___  ____  / / __ \/ ___/")
        print("          / ___/ __ `__ \/ __ \/ / / / /\__ \ ")
        print("         (__  ) / / / / / /_/ / / /_/ /___/ / ")
        print("        /____/_/ /_/ /_/\____/_/\____//____/  ")
        print("-------------\033[1;5;7mTINY-OS-FOR-TINY-COMPUTERS\033[0;1;33;44m------------\n\033[0m")

    def welcome(self):
        self.banner()
        self.lshw()
        
        print("\n\033[1mMemory:")
        self.free()
        print("\n\033[1mStorage:")
        self.df()

    def man(self,cmd=""):
        try:
            desc = self.user_commands_manual[cmd]
            print(f"\033[1m{cmd}\033[0m - {desc}")
        except:
            self.print_err("Man not available for command " + cmd)

    def help(self):
        print(self.name + " version " + self.version + " user commands:\n")

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

    def toggle_turbo(self):
        self.turbo = not self.turbo
        if self.turbo:
            freq = self.cpu_speed_range["turbo"]
        else:
            freq = self.cpu_speed_range["slow"]
        machine.freq(freq * 1000000)
        self.print_msg("CPU speed set to "+str(freq)+" Mhz")

    def cls(self):
         print("\033[2J")
         print("\033[H")

    def ls(self, mode="-l"):
        tsize=0
        for file in uos.listdir():
            tsize += self.info(file, mode)

        print("\nTotal: " + str(tsize) + " bytes")
        
    def info(self,filename="", mode="-a"):
        if not utls.file_exists(filename):
            self.print_err("File not found")
            return
        
        # Hiden file
        if mode!="-a":
            if filename[1]==".": return 0
        
        stat = utls.get_stat(filename)
        
        mode = stat[0]
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
        
        #TODO: Check show speed
        print(f"{fattr} {size:7} {utls.MONTH[localtime[1]]} " + \
              f"{localtime[2]:0>2} {localtime[4]:0>2} {localtime[5]:0>2} {filename}")
              
        #print('%s %7d %s %2d %02d:%02d %s' % (fattr, size, utls.MONTH[localtime[1]],
        #      localtime[2], localtime[4], localtime[5], filename))

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

    def py(self,filename=""):
        if filename == "":
            self.print_err("Specify a file name to run (without .py).")
            return
        exec(open(filename+".py").read())

    def exit(self):
        raise SystemExit

    def exe(self,command):
        exec(command)

    def pwd(self):
        print(uos.getcwd())
       
    def mkdir(self, path=""):
        uos.mkdir(path)
    
    def rmdir(self, path=""):
        uos.rmdir(path)
        
    def chdir(self, path=""):
        uos.chdir(path)
        
    def touch(self, filename="", c1="", c2="", c3=""):
        with open(filename, "a") as file:
            file.write(c1+c2+c3+"\n")

    def free(self, mode="-h"):
        gc.collect()
        
        f = gc.mem_free()
        a = gc.mem_alloc()
        t = f+a
        #p = '({0:.2f}%)'.format(f/t*100)
        p = f'({f/t*100:.2f}%)'
        
        if mode=="-h":
            #print('\033[0mTotal.:\033[1m %7d bytes' % (t))
            print(f'\033[0mTotal.:\033[1m {t:7} bytes')
            print(f'\033[0mAlloc.:\033[1m {a:7} bytes')
            print(f'\033[0mFree..:\033[1m {f:7} bytes {p}')
        else:
            d={"total": t, "alloc": a, "free": f, "%": p}
            print(d)
            
    def df(self, mode="-h", path="/"):
        
        bit_tuple = uos.statvfs(path)
        blksize = bit_tuple[0]  # system block size
        t = bit_tuple[2] * blksize
        f = bit_tuple[3] * blksize
        u = t - f
        
        if mode=="-h":
            print(f'\033[0mTotal space:\033[1m {t:8} bytes')
            print(f'\033[0mUsed space.:\033[1m {u:8} bytes')
            print(f'\033[0mFree space.:\033[1m {f:8} bytes')
        else:
            d={"total": t, "used": u, "free": f}
            print(d)
            
    def lshw(self, mode="-b"):
        print(f"\033[0mBoard:\033[1m {self.board}")
        print(f"\033[0mMicroPython:\033[1m {uos.uname().release}")
        print(f"\033[0m{self.name} :\033[1m {self.version} (size: {uos.stat('main.py')[6]} bytes)")
        print(f"\033[0mFirmware:\033[1m{uos.uname().version}")
        
        turbo_msg = f"\033[0mIn power-saving, \033[1mslow mode\033[0m. Use `turbo` to boost speed."
        if self.turbo:
            turbo_msg = "\033[0mIn \033[1mturbo mode\033[0m. Use `turbo` for slow mode."
        
        print(f"\033[0mCPU Speed:\033[1m{machine.freq()*0.000001}MHz {turbo_msg}")
        
        # Full hardware       
        if mode=="-f":
            try:
                with open("/etc/" + self.name + ".board", "r") as bcf:
                    bc=utls.load(bcf)
                    for e in bc.keys():
                        i=bc[e]
                        #TODO prettify
                        #print(f"{type(i)}")
                        #if type(i) is dict:
                        #    print(f"{e}: {i}")
                        #if type(i) is list:
                        #    print(f"{e}: {i}")
                        #else:
                        #    print(f"{e}: {i}")
                            
                        print(f"{e}: {i}")

            except Exception as ex:
                self.print_err("lshw error, " + str(ex))
                pass
        
    def led(self, cmd="on", lna="0"):
        ln=int(lna)
        
        # Test rgb leds pins with ln leds in each strip
        if cmd=="rgb":
            if ln < 1: return
            import neopixel
            for pn in self.rgb_led_pins:
                np = neopixel.NeoPixel(machine.Pin(pn), ln, bpp=4)
                for i in range(ln):
                    np[i] = (255, 0, 0, 5)
                    np.write()                
                    utime.sleep(.200)
                    np[i] = (0, 255, 0, 5)
                    np.write()                
                    utime.sleep(.200)
                    np[i] = (0, 0, 255, 5)
                    np.write()                
                    utime.sleep(.200)
                    np[i] = (0, 0, 0, 0)
                    np.write()
            return
        
        if ln < 0 or ln>len(self.system_leds)-1:
            self.print_err("Led not found.")
            return
        if cmd in ("on",""):
            self.system_leds[ln].value(1)
            return
        if cmd=="off":
            self.system_leds[ln].value(0)
            return
        if cmd=="boot":
            for led in self.system_leds:
                for _ in range(2):
                    led.value(1)
                    utime.sleep(0.1)
                    led.value(0)
                    utime.sleep(0.05)
            return
        
   # smolEDitor
    # Minimum viable text editor
    def ed(self, filename=""):
        self.page_size = 10
        self.file_edited = False
        print("Welcome to \033[7msmolEDitor\033[0m\nMinimum viable text editor for smol operating system")
        try:
            with open(filename,'r+') as file:
                if filename in self.protected_files:
                    self.print_err("Protected file. View only.")
                self.print_msg("Loaded existing "+filename+" file.")
                lines = file.readlines()
                line_count = len(lines)
                start_index = 0

                while True:
                    if start_index < line_count:
                        end_index = min(start_index + self.page_size,line_count)
                        print_lines = lines[start_index:end_index]

                        print("\033[7m    File:",filename,"Lines:",line_count," // `h` help, `b` back,`n` next page\033[0m")

                        for line_num,line in enumerate(print_lines,start=start_index + 1):
                            print(line_num,":",line.strip())

                    user_ed_input = input("\ned $: ")

                    if user_ed_input =="quit":
                        if self.file_edited:
                            self.print_msg("file was edited, `save` it first or write `quit!`")
                        else:
                            self.print_msg("smolEDitor closed")
                            break

                    if user_ed_input == "quit!":
                        self.print_msg("smolEDitor closed")
                        break

                    if user_ed_input == "help":
                        self.man(self.ed_commands_manual)

                    if user_ed_input == "append":
                        line_count += 1
                        lines.append("")

                    if user_ed_input == ">":
                        if start_index+self.page_size < line_count:
                            start_index += self.page_size
                        else:
                            self.print_msg("There is no next page. This is the last page.")

                    if user_ed_input == "<":
                        if start_index-self.page_size >= 0:
                            start_index -= self.page_size
                        else:
                            self.print_msg("Can not go back, it is a first page already.")

                    if user_ed_input in ("save","write"):
                        if filename in self.protected_files:
                            self.print_err("Protected file")
                        else:
                            self.print_err("Saving not implemented yet")

                    parts = user_ed_input.split(" ",1)
                    if len(parts) == 2:
                        if parts[0] == "append":
                            new_lines = int(parts[1])
                            line_count += new_lines
                            for _ in range(new_lines):
                                lines.append("")
                        else:
                            if filename in self.protected_files:
                                self.print_err("Protected file")
                            else:
                                line_number = int(parts[0])
                                new_content = parts[1]                                
                                if line_number > 0 and line_number < line_count:
                                    lines[line_number - 1] = new_content + "\n"
                                else:
                                    self.print_err("Invalid line number")
                        self.file_edited = True

        except OSError:
            if filename == "":
                self.print_err("Provide an existing file name after the `ed` command.")
            else:
                self.print_err("Failed to open the file.")
            pass

smol = smolOS()
