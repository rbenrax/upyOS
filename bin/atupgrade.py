from esp_at import ModemManager
import os
import machine
import utime

import utls
import sdata

# Source branches
mainb = f'https://raw.githubusercontent.com/rbenrax/upyOS/refs/heads/main/'
testb = f'https://raw.githubusercontent.com/rbenrax/upyOS/refs/heads/test/'

def pull(f_path, url):

    try:
        _, _, host, path = url.split('/', 3)
        solicitud = f"GET /{path} HTTP/1.0\r\nHost: {host}\r\nUser-Agent: upyOS\r\n\r\n"
        mm = ModemManager("modem0")
        #mt.sctrl = True
        #mt.scmds = True
        #mm.sresp = True
        #mm.timming = True
        
        mm.create_conn(host, 443, "SSL", keepalive=60) 
        sts, ret = mm.send_data_transp(solicitud, 5)
        
        f = open(f_path, 'w')
        mm.rcvDATA_tofile(f, timeout=8.0)
        f.close()
        
        #sts, body, headers = mm.rcvDATA(0, True, 15)
        #if sts:
        #    #print(body)
        #    f = open(f_path, 'w')
        #    f.write(body)
        #    f.close()
        #else:
        #    print(f"- Error downloading {f_path}")
            
        #mm.close_conn() # if not closed by server
 
    except Exception as e:
        print(f"\natupgrade/pull: {f_path} - {str(e)}")

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

    print("upyOS OTA Upgrade 2.0 (ESP-AT), \nDownloading upgrade list ", end="")
    
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
            fp = f.readline()
            
            if not fp: break
            if fp.strip()=="": continue   # Empty lines skipped
            if fp.strip().startswith("#"): continue # Commanted lines skipped
            
            fp = fp[:-1] # remove ending CR
            if "v" in mod:
                print(fp, end=", ")
            else:
                print(".", end="")
            pull(fp, url_raw + fp[1:])
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
