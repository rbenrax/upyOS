import os
import urequests
import machine
import utime
import usocket
import ssl

import utls
import sdata
import sys

# Source branches
mainb = f'https://raw.githubusercontent.com/rbenrax/upyOS/main/'
testb = f'https://raw.githubusercontent.com/rbenrax/upyOS/refs/heads/test/'

def pull(f_path, url):    
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
    
def __main__(args):

    mod="" 
    for i in args:
        if i[0]=="-": mod +=i [1:]

    for p in sdata.procs:
        if p.isthr:
            print("Stop all process before upgrade")
            return

    if "h" in mod:
        print("Upgrade upyOS from git repository\nUsage: upgrade <options>:-f quite mode, -r reboot after upgrade, -v view file list, -t test branch")
        return

    print("upyOS OTA Upgrade 2.0, \nDownloading upgrade list ", end="")
    
    if "t" in mod:
        url_raw = testb # test
        print("from test branch", end="")
    else:
        url_raw = mainb # Default main
        print("from main branch", end="")
        
    uf="/etc/upgrade2.inf"
    pull(uf, url_raw + uf[1:])
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
    
    ftu=int(end[1]) # files to upgrade

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
    with open(uf, 'r') as f:
        while True:
            ln = f.readline()
            
            if not ln: break
            if ln.strip()=="": continue   # Empty lines skipped
            if ln.strip().startswith("#"): continue # Comment lines skipped
            
            tmp = ln.split(",")
            
            fp = fp[0]
            fs = ln[1]            
            
            if "v" in mod:
                print(fp, end=", ")
            else:
                print(".", end="")
                
            pull(fp, url_raw + fp)
            
            cont+=1
            
    os.remove(uf)
    
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
