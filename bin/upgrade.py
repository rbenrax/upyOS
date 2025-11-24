import os    
import machine
import utime

try:
    import urequests
    import usocket
    import ssl
except:
    print("Try atupgrade with esp-at modem instead")

import hashlib
import utls
import sdata
import sys
import time

# Source branches
mainb = f'https://raw.githubusercontent.com/rbenrax/upyOS/refs/heads/main'
testb = f'https://raw.githubusercontent.com/rbenrax/upyOS/refs/heads/test'

def pull(url, f_path):    
    s = None
    ssl_socket = None
    
    try:
        _, _, host, path = url.split('/', 3)
        
        s = usocket.socket()
        ai = usocket.getaddrinfo(host, 443)
        addr = ai[0][-1]
        s.connect(addr)
        ssl_socket = ssl.wrap_socket(s)
        
        solicitud = f"GET /{path} HTTP/1.0\r\nHost: {host}\r\nUser-Agent: upyOS\r\n\r\n"
        ssl_socket.write(bytes(solicitud, 'utf8'))

        # Leer headers línea por línea
        header_buffer = b''
        headers_complete = False
        
        while not headers_complete:
            chunk = ssl_socket.read(1)
            if not chunk:
                break
            header_buffer += chunk
            if header_buffer.endswith(b'\r\n\r\n'):
                headers_complete = True

        # Ahora leer el contenido del archivo
        with open(f_path, 'wb') as f:  # Abrir en modo binario
            while True:
                chunk = ssl_socket.read(512)
                if not chunk:
                    break
                f.write(chunk)
                
    except Exception as e:
        print(f"\nupgrade/pull: {f_path} - {str(e)}")
    finally:
        if ssl_socket: ssl_socket.close()
        if s: s.close()
    
def hash_sha1(filename):
    if not utls.file_exists(filename): return ""
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

    print("upyOS OTA Upgrade 2.0, \nDownloading upgrade list ", end="")
    
    if "t" in mod:
        url_raw = testb # test
        print("from test branch", end="")
    else:
        url_raw = mainb # Default main
        print("from main branch", end="")
        
    uf="/etc/upgrade.inf"
    if utls.file_exists(uf):
        os.remove(uf)
    pull(url_raw + uf, uf)
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
    cntup=0
    with open(uf, 'r') as f:
        while True:
            ln = f.readline()
            
            if not ln: break
            if ln.strip()=="": continue   # Empty lines skipped
            if ln.strip().startswith("#"): continue # Commanted lines skipped
            
            tmp = ln.split(",")
            
            fp = tmp[0]
            fs = int(tmp[1])
            
            #print(f"File: {fp} {fs}")
            
            hsh=None
            if len(tmp) > 2:
                hsh = tmp[2]
            
            if "v" in mod:
                print(fp, end=", ")
            else:
                print(".", end="")
            
            if hsh:
                lhsh = hash_sha1(fp)
                if hsh == lhsh:
                    cont+=1
                    continue
            
            ptini = time.ticks_ms()
            
            upgr=False
            tmpfsz=0
            tmpf = "/tmp/ptf_file.tmp"
            for r in range(3):
                
                #if utls.file_exists(tmpf):
                #    print(f"{tmpf} {utls.file_exists(tmpf)}")
                #    os.remove(tmpf)
                
                pull(url_raw + fp, tmpf)
                
                time.sleep(.3)
                
                stat = utls.get_stat(tmpf)
                tmpfsz = stat[6]
                
                if tmpfsz == fs or "o" in mod: # Overwrite diffs
                    if utls.file_exists(fp):
                        os.remove(fp)
                    os.rename(tmpf, fp)
                    upgr=True
                    cont+=1
                    break

            ptfin = time.ticks_diff(time.ticks_ms(), ptini)
            #print(f" <-> S2: {size2} {ptfin}ms")

            if not upgr:
                print(f"\nDownload error: {fp} {fs} != {tmpfsz}")
                print(f"upgrade.inf file may not be up to date")
                if not "i" in mod: break # ignore and show errors
            else:
                cntup+=1
            
#     os.remove(uf)

    #print(str(ftu))
    #print(str(cont))
    
    if ftu == cont:
        print("]OK\n100% Upgrade complete.")
        print(f"{cntup} Upgraded files")
    else:
        print("]Error in upgrade,\nUpgrade not complete.")
        
    utime.sleep(2)
    
    if "r" in mod:
        print("Rebooting...")
        utime.sleep(2)
        machine.soft_reset()
