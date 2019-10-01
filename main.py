import socket
import sys
import argparse
import time
import os
import sys
import threading

FLAGS = None
BCAST_PORT = 12345
DATA_PORT = 54321

class Broadcast():
    def __init__(self):
        self.HOSTNAME = socket.gethostname()
        self.HOST_SET = set()
        self.runningFlag = True
        self.recv_socket = None
        self.t_send = threading.Thread(target=self.send_bcast)
        self.t_recv = threading.Thread(target=self.recv_bcast)
        self.t_send.start()
        self.t_recv.start()
        
    def send_bcast(self):
        dest = ('<broadcast>', BCAST_PORT)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        while self.runningFlag:
            s.sendto(self.HOSTNAME.encode(), dest)
            time.sleep(1)
        s.close()

    def recv_bcast(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.recv_socket = s
        s.bind(('0.0.0.0', BCAST_PORT))
        s.settimeout(1)
        while self.runningFlag:
            try:
                host, addr = s.recvfrom(BCAST_PORT)
                self.HOST_SET.add((host.decode(), addr[0]))
            except socket.timeout:
                continue
            except:
                break
        s.close()

    def get_HOST_LIST(self):
        return list(self.HOST_SET)

    
class FileTransfer():
    def __init__(self):
        pass
    
    def recv_file(self, ip):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((ip, DATA_PORT))
        s.listen(1)
        conn, _ = s.accept()
        filename = conn.recv(1048576)
        filename = filename.decode()
        conn.close()
        conn, _ = s.accept()
        f = open(filename, 'wb')
        while True:
            data = conn.recv(1024)
            if not data:
                break
            f.write(data)
        f.close()
        conn.close()
        s.close()

    def send_file(self, ip, filename):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, DATA_PORT))
        f = open(filename, 'rb')
        s.send(filename.encode())
        s.close()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, DATA_PORT))
        l = f.read(1024)
        while (l):
            s.send(l)
            l = f.read(1024)
        f.close()
        s.close()



current_hosts = []
hadBrowsed = False

def get_hosts(bcast):
    global current_hosts
    current_hosts = bcast.get_HOST_LIST()

def print_hosts():
    global current_hosts
    global hadBrowsed
    hadBrowsed = True
    print("--------------------------------")
    for i in range(1, len(current_hosts)+1):
        print(str(i) + ": " + str(current_hosts[i-1]))
    print("--------------------------------")

if __name__ == "__main__":
    bcast = Broadcast()
    filetransfer = FileTransfer()

    while True:
        command = input("\na: list hosts\nb: send file\nc: receive file\nz: exit\n")
        if command == 'a':
            get_hosts(bcast)
            print_hosts()
        elif command == 'b':
            if not hadBrowsed:
                print("Please list hosts first.\n")
                continue
            host = int(input("Enter host ID:\n")) - 1
            if host < 0 or host > len(current_hosts):
                print("Wrong host ID number!")
                continue
            filename = input("Enter file path:\n")
            filetransfer.send_file(current_hosts[host][1], filename)
        elif command == 'c':
            filetransfer.recv_file('0.0.0.0')
        elif command == 'z':
            bcast.runningFlag = False
            bcast.t_recv.join()
            bcast.t_send.join()
            sys.exit(0)
        else:
            print("Wrong input!")