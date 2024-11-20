import socket
import sys
import struct
import time
import csv
import json
from threading import Thread

def setup_udp_opal(port):
    localIP = "127.0.0.1"
    localPort = port
    bufferSize = 1024

    # create datagram socket
    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    # Bind to address and ip
    UDPServerSocket.bind((localIP, localPort))

    print("UDP server up and listening ok")

    return UDPServerSocket

def run_udp_opal(UDPServerSocket):
    print(UDPServerSocket)
    bufferSize = 32
    while True:
        try:
            bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
            address = bytesAddressPair[1]
            message = struct.unpack('@fffffff', bytesAddressPair[0])
            print(message, address)
        except Exception:
            print(Exception)
            print('error')
            time.sleep(1)
            return
        
if __name__ == '__main__':
    # sock1 = setup_udp_opal(21002)
    sock2 = setup_udp_opal(22002)
    # .....
    # thread1 = Thread(target=run_udp_opal, args=(sock1,))
    thread2 = Thread(target=run_udp_opal, args=(sock2,))
    # .....
    # thread1.start()
    thread2.start()
    # .....