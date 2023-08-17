# wget for octopusLAB MicroPython uPyShell
# copyright (c) 2020 Milan Spacek
# License: MIT

# wget https://www.octopusengine.org/api/text123.txt [subdir]
# default subdir: "download"

__version__ = "1.0.0"

def wget(url="",path="/download"):
    from shell.new_urequests import get
    from os import mkdir
    from gc import collect
    debug = False
    filename = url.split("/")[-1]

    valid_chars = '-_.()abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    correc_filename = ''.join(c for c in filename if c in valid_chars)

    if filename != correc_filename:
        print("Wrong filename corrected:" + correc_filename)

    if path != "":
        try:
            if path.endswith('/'):
                path = path[:-1]
            os.mkdir(path)
        except:
            pass
        path = path + "/"

    collect()
    try:
        if debug: print("get")
        res = get(url, stream = True)
        if debug: print("get done")
        if debug: print(res.status_code)
        collect()
        if res.status_code == 200:
            print("opening file:", path+correc_filename)
            f = open(path+correc_filename, 'w')
            if debug: print("opened file")
            while True:
                if debug: print("reading chunk")
                chunk = res.raw.read(256)
                if debug: print("writing chunk")
                #if debug: print(chunk)
                f.write(chunk)
                if debug: print("chunk writen")
                if not chunk:
                    break
            f.close()
            print("Done")
        elif res.status_code == 404:
            print("File not found")
        else:
            print("Error status:", res.status_code)
    except OSError as e:
        if e.args[0] == -202:
            print("wget: unable to resolve host address")
        else:
            print("OSError, exception: {0}".format(e))
    except Exception as e:
        print("Error, exception: {0}".format(e))
