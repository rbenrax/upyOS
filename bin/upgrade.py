import os
import urequest
import machine

user='rbenrax'
repository='upyOS'
default_branch = 'main'
    
#------

#giturl = f'https://github.com/{user}/{repository}'
url_tree = f'https://api.github.com/repos/{user}/{repository}/git/trees/{default_branch}?recursive=1'
url_raw = f'https://raw.githubusercontent.com/{user}/{repository}/master/'

def pull_git_tree(u_tree):
    headers = {'User-Agent': 'upyOS'} 
    r = urequests.get(u_tree, headers=headers)
    print(r.content.decode('utf-8'))

def pull(f_path, raw_url):

    try:
  
        headers = {'User-Agent': 'upyOS'} 
        r = urequests.get(raw_url, headers=headers)
  
        with open(f_path, 'w') as f:
            f.write(r.content.decode('utf-8'))
            print(r.content.decode('utf-8'))
            
    except Exception as ex:
        print('pull error: ' + ex)
    
def __main__(args):

    if len(args) == 1 and args[0]=="--h":
        print("Upgrade upyOS from git repository\nUsage: upgrade")
        return
    else:
        uf="/upgrade.inf"
        pull(uf, url_raw + uf[1:])
        
        print("Upgrading from upyOS git repsitory, wait...")
        with open(uf, 'r') as f:
            while True:
                fp=f.readline()
                if not fp: break
                print(fp)
                fn=fp.split("/")[-1]
                pull(fp, url_raw + fn)

   
        

        
