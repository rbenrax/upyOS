import os
import urequests
import machine
import utime
import usocket
import ssl

import utls
import sdata

url_raw = f'https://raw.githubusercontent.com/rbenrax/upyOS/main/'

def pull(f_path, url):    
    
    s=None
    ssl_socket=None
    
    try:
        _, _, host, path = url.split('/', 3)
        #print(f"{f_path} {url} {host} {path}")
        
        s = usocket.socket()
        
        ai = usocket.getaddrinfo(host, 443)
        addr = ai[0][-1]
        
        s.connect(addr)
        
        ssl_socket = ssl.wrap_socket(s)
        
        solicitud = f"GET /{path} HTTP/1.0\r\nHost: {host}\r\nUser-Agent: upyOS\r\n\r\n"
        
        ssl_socket.write(bytes(solicitud, 'utf8'))

        headers_received = False

        with open(f_path, 'w') as f:            
            while True:
                chunk = ssl_socket.read(512)
                if not chunk:
                    break
                
                #print(chunk.decode('utf8'))
                if not headers_received:
                    end_of_headers = chunk.find(b'\r\n\r\n')
                    if end_of_headers != -1:
                        headers_received = True
                        #f.write(chunk[end_of_headers + 4:].decode('utf-8'))
                        f.write(chunk[end_of_headers + 4:].decode('utf-8', 'ignore'))
                    else:
                        continue
                else:
                    #f.write(chunk.decode('utf-8'))
                    f.write(chunk.decode('utf-8', 'ignore'))
    except OSError as osr:
        print(f"\nupgrade/pull: {f_path} - {str(osr)}")
    finally:
        if ssl_socket: ssl_socket.close()
        if s: s.close()

    return
    
def __main__(args):

    mod="" 
    for i in args:
        if i[0]=="-": mod +=i [1:]

    for p in sdata.procs:
        if p.isthr:
            print("Stop all process before upgrade")
            return

    if "h" in mod:
        print("Upgrade upyOS from git repository\nUsage: upgrade <options>:-f quite mode, -r reboot after upgrade, -v view file list")
        return

    print("upyOS OTA Upgrade, \nDownloading upgrade list...", end="")
    uf="/etc/upgrade.inf"
    pull(uf, url_raw + uf[1:])
    print(", OK")
    
    if not utls.file_exists(uf):
        print("No upgrade file available, system can not be upgraded")
        return
        
    if not "f" in mod:
        r = input("Confirm upyOS upgrade (y/N)? ")
        if r!="y":
            print("Upgrade canceled")
            return
          
    print("Upgrading from upyOS github repository, wait...")
    print("[", end="")
    with open(uf, 'r') as f:
        while True:
            fp=f.readline()
            if not fp: break
            fp=fp[:-1] # remove ending CR
            if "v" in mod:
                print(fp, end=", ")
            else:
                print(".", end="")
            pull(fp, url_raw + fp[1:])
            
    os.remove(uf)
    print("]OK\n100% Upgrade complete")
    utime.sleep(2)
    
    if "r" in mod:
        print("Rebooting...")
        utime.sleep(2)
        machine.soft_reset()

