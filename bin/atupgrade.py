from esp_at import ModemManager
import os
import machine
import utime

import utls
import sdata
import time

# Source branches
mainb = f'https://raw.githubusercontent.com/rbenrax/upyOS/refs/heads/main/'
testb = f'https://raw.githubusercontent.com/rbenrax/upyOS/refs/heads/test/'

def pull(mm, f_path, url):

    try:
 
        sts = mm.http_to_file(url, f_path)
        if not sts:
            print(f"- Error downloading {f_path}")
        return sts
 
    except Exception as e:
        print(f"\natupgrade/pull: {f_path} - {str(e)}")
        return False

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

    mm = ModemManager("modem0")
    #mm.sctrl = True
    #mm.scmds = True
    #mm.sresp = True
    #mm.timming = True

    print("upyOS OTA Upgrade 2.0 (ESP-AT), \nDownloading upgrade list ", end="")
    
    if "t" in mod:
        url_raw = testb # test
        print("from test branch", end="")
    else:
        url_raw = mainb # Default main
        print("from main branch", end="")
        
    uf="/etc/upgrade2.inf"
    pull(mm, uf, url_raw + uf[1:])
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
        print("Error ungrade file, see /etc/upgrade2.inf")

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
    
            #if fp == "/libx/esp_at.py":
            #    print(f"Saltando {fp}")
            #    cont+=1
            #    continue
    
            ptini = time.ticks_ms()
    
            stat = utls.get_stat(fp)            
            size1 = stat[6]
            #print(f"{fp} S1: {size1}", end="")
            
            pull(mm, fp, url_raw + fp[1:])
            
            stat = utls.get_stat(fp)            
            size2 = stat[6]
            
            #ptfin = time.ticks_diff(time.ticks_ms(), ptini)
            #print(f" <-> S2: {size2} {ptfin}ms")

            cont+=1

            if size1 != size2:
                print(f"Error in file: {fp}")
                break
            
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
