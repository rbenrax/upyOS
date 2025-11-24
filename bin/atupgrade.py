from esp_at import ModemManager
import os
import machine
import utime

import utls
import sdata


# Source branches
mainb = f'https://raw.githubusercontent.com/rbenrax/upyOS/refs/heads/main'
testb = f'https://raw.githubusercontent.com/rbenrax/upyOS/refs/heads/test'

def pull(mm, url, f_path):

    try:
 
        sts = mm.http_get_to_file_t(url, f_path)
        if not sts:
            print(f"- Error downloading {f_path}")
        return sts
 
    except Exception as e:
        print(f"\natupgrade/pull: {f_path} - {str(e)}")
        return False

def hash_sha1(filename):
    h = hashlib.sha1()
    with open(filename, 'rb') as f:
        while True:
            chunk = f.read(512)
            if not chunk:
                break
            h.update(chunk)
    return h.digest().hex()

def __main__(args):

    mod="" 
    for i in args:
        if i[0]=="-": mod +=i [1:]

    for p in sdata.procs:
        if p.isthr:
            print("Stop all process before upgrade")
            return

    if "h" in mod:
        print("Upgrade upyOS from git repository")
        print("Usage: upgrade <options>:-f quite mode, -r reboot after upgrade, -v view file list")
        print(", -t test branch, -i ignore errors, -o overwrite diffs")
        return

    print("upyOS OTA Upgrade 2.0 (ESP-AT), \nDownloading upgrade list ", end="")
    
    if "t" in mod:
        url_raw = testb # test
        print("from test branch", end="")
    else:
        url_raw = mainb # Default main
        print("from main branch", end="")
    
    mm = ModemManager("modem0")
    #mm.sctrl = True
    #mm.scmds = True
    #mm.sresp = True
    #mm.timming = True

    if not mm.modem:
        print("\nError: No modem")
        return

    # Connection
    if not mm.create_url_conn(url_raw, keepalive=120):
        print("\nError: Cant connect")
        return
    
    mm.atCMD("ATE0") # Echo off
    mm.atCMD("AT+CIPMODE=1") # Transmissnon type 1
    mm.send_passthrow() # Send for passthrow
    
    uf="/etc/upgrade.inf"
    if utls.file_exists(uf):
        os.remove(uf)
    pull(mm, url_raw + uf, uf)
    print(", OK") 
    
    if not utls.file_exists(uf):
        print("No upgrade file available, system can not be upgraded")
        return

    ini=None
    end=None
    with open(uf, 'r') as f:
        for l in f:
            if l.startswith('#upyOS'):
                ini = l.strip().split(',')
            elif l.startswith('#files'):
                end = l.strip().split(',')

    print()
    #print(ini)
    #print(end)
    
    if len(end) > 1:
        ftu=int(end[1]) # files to upgrade
    else:
        print("Error ungrade file, see /etc/upgrade.inf")

    if not "f" in mod:
        print(f"upyOS current version: {sdata.version}")
        print(f"upyOS new version: {ini[1]} ({ini[2]})" )
        r = input("Confirm upgrade (y/N)? ")
        if r!="y":
            print("Upgrade canceled.")
            return
         
    print("Upgrading from upyOS github repository, wait...")
    print("[", end="")
    
    cont=0
    with open(uf,'r') as f:
        while True:
            ln = f.readline()
            
            if not ln: break
            if ln.strip()=="": continue   # Empty lines skipped
            if ln.strip().startswith("#"): continue # Commanted lines skipped
            
            tmp = ln.split(",")
            
            fp = tmp[0]
            fs = int(tmp[1])
            
            hsh=None
            if len(tmp) == 3:
                hsh = tmp[2]
            
            #print(f"File: {fp} {fs}")
            
            if "v" in mod:
                print(fp, end=", ")
            else:
                print(".", end="")
            
            if hsh:
                lhsh = hash_sha1(fp)
                if hsh == lhsh:
                    print("p1")
                    cont+=1
                    continue
            
            print("p2")
            upgr=False
            tmpfsz=0
            for r in range(3):
                tmpf = "/tmp/ptf_file.tmp"
                
                if utls.file_exists(tmpf):
                    os.remove(tmpf)
                    
                pull(mm, url_raw + fp, tmpf)
                
                stat = utls.get_stat(tmpf)           
                tmpfsz = stat[6]
                
                if tmpfsz == fs or "o" in mod: # Overwrite diffs
                    if utls.file_exists(fp):
                        os.remove(fp)
                    os.rename(tmpf, fp)
                    upgr=True
                    cont+=1
                    break

            if not upgr:
                print(f"\nError descarga: {fp} src: {fs} != dest: {tmpfsz}")
                print(f"upgrade.inf file may not be up to date")
                if not "i" in mod: break # ignore and show errors

    #os.remove(uf) 

    # Close connectiopn
    if mm.tcp_conn: 
        utime.sleep(1)
        mm.modem.write("+++")
        utime.sleep(1)
        mm.atCMD("AT+CIPMODE=0", 3)
        
        mm.close_conn()  
        mm.atCMD("ATE1", 2)    
    
    #print(str(ftu))
    #print(str(cont))
    
    if ftu == cont:
        print("]OK\n100% Upgrade complete.")
    else:
        print("]Error in upgrade,\nUpgrade not complete.")
        
    utime.sleep(2)
    
    if "r" in mod:
        print("Rebooting...")
        utime.sleep(2)
        machine.soft_reset()
