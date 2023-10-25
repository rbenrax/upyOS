# this code is from uftpserver (https://github.com/cpopp/MicroFTPServer/tree/master/uftp).
# there's no license so I used MIT and then...
# packed it into a class, added missing FTP commands, and added the threading
import socket
import network
import os
import _thread
import gc

DATA_PORT = 13333

class FtpTiny:
    '''This class creates a very tiny FTP server in a thread
        x = ftptiny.FtpTiny()
        x.start()
        x.stop()'''
    def __init__(self) :
        self.dorun = True
        self.isrunning = False
        self.cwd = os.getcwd()
        self.ftpsocket = None
        self.datasocket = None
        self.dataclient = None

    def start_listen(self) :
        # the two sockets are the persistant and the pasv sockets
        # so this requires pasv
        self.ftpsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.datasocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ftpsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.datasocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.ftpsocket.bind(socket.getaddrinfo("0.0.0.0", 21)[0][4])
        self.datasocket.bind(socket.getaddrinfo("0.0.0.0", DATA_PORT)[0][4])
        self.ftpsocket.listen(1)
        self.datasocket.listen(1)
        self.datasocket.settimeout(10)
        self.lastpayload = ''

    def send_list_data(self, client):
        for file in os.listdir(self.cwd):
            stat = os.stat(self.get_absolute_path(file))
            file_permissions = "drwxr-xr-x" if (stat[0] & 0o170000 == 0o040000) else "-rw-r--r--"
            file_size = stat[6]
            description = "{}    1 owner group {:>13} Jan 1  1980 {}".format(file_permissions, file_size, file)
            self.sendcmdline(client, description)

    def send_file_data(self, path, client):
        with open(path) as file:
            chunk = file.read(128)
            while len(chunk) > 0:
                client.sendall(chunk)
                if len(chunk) == 128:
                    chunk = file.read(128)
                else:
                    chunk = []

    def save_file_data(self, path, client):
        client.settimeout(.5)
        with open(path, "w") as file:
            try:
                chunk = client.recv(128)
                while chunk and len(chunk) > 0:
                    file.write(chunk)
                    if len(chunk) == 128 :
                        chunk = client.recv(128)
                    else :
                        chunk = None # done?
            except Exception as ex:
                pass

    def get_absolute_path(self, payload):
        # if it doesn't start with / consider
        # it a relative path
        rslt = payload
        if not payload.startswith("/"):
            if len(self.cwd) > 1 :
                rslt = self.cwd + "/" + payload
            else :
                rslt = self.cwd + payload
        # and don't leave any trailing /
        if len(rslt) > 1 :
            return rslt.rstrip("/")
        return rslt

    def stop(self):
        self.dorun = False
        self.thread = 0

    def start(self):
        if not self.isrunning :
            self.dorun = True
            tid = _thread.start_new_thread(runserver, (self, ))
            self.thread = tid
        else :
            print("An instance is already running.")

    def sendcmdline(self, cl, txt) :
        cl.sendall(txt)
        cl.sendall("\r\n")

    def closeclient(self) :
        if self.dataclient :
            self.dataclient.close()
            self.dataclient = None

    def client(self, cl) :
        return self.dataclient if self.dataclient else cl

    def _handle_command(self, cl, command, payload) :
        if command == "USER":
            self.sendcmdline(cl, "230 Logged in.")
        elif command == "SYST":
            self.sendcmdline(cl, "215 ESP32 MicroPython")
        elif command == "SYST":
            self.sendcmdline(cl, "502")
        elif command == "PWD":
            self.sendcmdline(cl, '257 "{}"'.format(self.cwd))
        elif command == "CWD":
            path = self.get_absolute_path(payload)
            try:
                os.chdir(path)
                self.sendcmdline(cl, '250 Directory changed successfully')
            except:
                self.sendcmdline(cl, '550 Failed to change directory')
            finally:
                self.cwd = os.getcwd()
        elif command == "EPSV":
            self.sendcmdline(cl, '502')
        elif command == "TYPE":
            # probably should switch between binary and not
            self.sendcmdline(cl, '200 Transfer mode set')
        elif command == "SIZE":
            path = self.get_absolute_path(payload)
            try:
                size = os.stat(path)[6]
                self.sendcmdline(cl, '213 {}'.format(size))
            except:
                self.sendcmdline(cl, '550 Could not get file size')
        elif command == "QUIT":
            self.sendcmdline(cl, '221 Bye.')
        elif command == "PASV":
            addr = network.WLAN().ifconfig()[0]
            self.sendcmdline(cl, '227 Entering Passive Mode ({},{},{}).'.format(addr.replace('.',','), DATA_PORT>>8, DATA_PORT%256))
            self.dataclient, data_addr = self.datasocket.accept()
            print("FTP Data connection from:", data_addr)
        elif command == "LIST":
            try:
                # list folder contents
                self.send_list_data(self.client(cl))
                self.closeclient()
                self.sendcmdline(cl, "150 Here comes the directory listing.")
                self.sendcmdline(cl, "226 Listed.")
            except:
                self.sendcmdline(cl, '550 Failed to list directory')
            finally:
                self.closeclient()
        elif command == "RETR":
            try:
                # send a file to the client
                self.send_file_data(self.get_absolute_path(payload), self.client(cl))
                self.closeclient()
                self.sendcmdline(cl, "150 Opening data connection.")
                self.sendcmdline(cl, "226 Transfer complete.")
            except:
                self.sendcmdline(cl, '550 Failed to send file')
            self.closeclient()
        elif command == "STOR":
            try:
                # receive a file and save to disk
                self.sendcmdline(cl, "150 Ok to send data.")
                self.save_file_data(self.get_absolute_path(payload), self.client(cl))
                self.closeclient()
                print("Finished receiving file")
                self.sendcmdline(cl, "226 Transfer complete.")
            except Exception as ex:
                print("Failed to receive file: " + str(ex))
                self.sendcmdline(cl, '550 Failed to send file')
            finally:
                print("Finally closing dataclient")
                self.closeclient()
        elif command == "DELE":
            try:
                # delete a file
                path = self.get_absolute_path(payload)
                os.remove(path)
                print("Deleted file: " + path)
                self.sendcmdline(cl, "250 File deleted ok.")
            except Exception as ex:
                print("Failed to delete file: " + str(ex))
                self.sendcmdline(cl, '550 Failed to delete file.')
            finally:
                self.closeclient()
        elif command == "MKD":
            try:
                # create a folder
                path = self.get_absolute_path(payload)
                os.mkdir(path)
                print("Create folder: " + path)
                self.sendcmdline(cl, "257 Path created ok.")
            except Exception as ex:
                print("Failed to create folder: " + str(ex))
                self.sendcmdline(cl, '550 Failed to create folder.')
            finally:
                self.closeclient()
        elif command == "RMD":
            try:
                # delete a folder
                path = self.get_absolute_path(payload)
                os.rmdir(path)
                print("Deleted folder: " + path)
                self.sendcmdline(cl, "250 Folder deleted ok.")
            except Exception as ex:
                print("Failed to delete folder: " + str(ex))
                self.sendcmdline(cl, '550 Failed to delete file.')
            finally:
                self.closeclient()
        elif command == "CDUP":
            try:
                # change to parent folder
                if self.cwd and len(self.cwd) > 1 :
                    paths = self.cwd.split('/')
                    xpat = '/' + '/'.join(paths[:-1])
                else :
                    xpat = '/'
                os.chdir(xpat)
                self.cwd = xpat
                print("Go to parent: " + xpat)
                self.sendcmdline(cl, "250 Went to parent folder.")
            except Exception as ex:
                print("Failed to delete folder: " + str(ex))
                self.sendcmdline(cl, '550 Failed to go to parent.')
            finally:
                self.closeclient()
        elif command == "RNFR":
                # rename file start...
                self.lastpayload = payload
                self.sendcmdline(cl, "226 Starting rename.")
        elif command == "RNTO":
            if self.lastpayload :
                try:
                    # rename file end...
                    os.rename(self.lastpayload, payload)
                    self.sendcmdline(cl, "250 Renamed file.")
                except Exception as ex:
                    print("Failed to rename file: " + str(ex))
                    self.sendcmdline(cl, '550 Failed to rename file.')
                finally:
                    self.closeclient()
                    self.lastpayload = None
        else:
            self.sendcmdline(cl, "502 Unsupported command.")
            print("Unsupported command {} with payload {}".format(command, payload))

    # called by the threader
    def dolisten(self):
        self.isrunning = True
        try:
            self.start_listen()
            while self.dorun:
                cl, remote_addr = self.ftpsocket.accept()
                cl.settimeout(300)
                try:
                    print("FTP connection from:", remote_addr)
                    self.sendcmdline(cl, "220 Hello. Welcome to FtpTiny.")
                    # --- here's the command loop
                    # since it's waiting at readline this doesn't end after stop() unless you
                    # send a command
                    while self.dorun:
                        data = cl.readline().decode("utf-8").replace("\r\n", "")
                        if len(data) <= 0:
                            print("Client is gone")
                            break

                        command, payload = (data.split(" ") + [""])[:2]
                        command = command.upper()

                        print("Command={}, Payload={}".format(command, payload))
                        self._handle_command(cl, command, payload)
                        # we use up memory here, so deal with it
                        gc.collect()
                    # --- end of command loop
                except Exception as ex :
                    print(str(ex))
                finally:
                    print("Closing dataclient socket")
                    cl.close()
        except Exception as ex :
            print("TinyFtp error: "  + str(ex))
        finally:
            self.isrunning = False
            self.closeclient()
            self.datasocket.close()
            self.ftpsocket.close()
            # we use up memory here, so deal with it
            gc.collect()

# our thread calls this which then listens
def runserver(myself):
    myself.dolisten()
