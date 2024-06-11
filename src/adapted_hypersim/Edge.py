import os
import socket
import struct
import sys
import threading
import time

from utils import get_type_values
hypersimDir = r"C:\\OPAL-RT\\HYPERSIM\\hypersim_2024.1.0.o39"
if not os.path.isdir(hypersimDir):
    print("INVALID HYPERSIM DIRECTORY SPECIFIED IN THE SCRIPT")
    exit(1)
sys.path.append(os.path.join(hypersimDir, 'Windows', 'HyApi', 'python'))
import HyWorksApiGRPC as HyWorksApi


class Edge():
    def __init__(self, label, tcp_sensors_port, udp_sensors_port, actuator_port):
        self.label = label
        self.local_IP = '0.0.0.0'
        self.remote_IP = '172.31.144.1'

        self.hyp_udp_sensors_port = int(udp_sensors_port) + 2
        self.hyp_tcp_sensors_port = int(tcp_sensors_port) + 2
        self.hyp_actuators_port = int(actuator_port) + 2
        self.udp_sensors_port = int(udp_sensors_port)
        self.tcp_sensors_port = int(tcp_sensors_port)
        self.actuators_port = int(actuator_port)

        self.udp_sensors_socket = self.setup_udp_client() #TODO: check multiprocessing
        self.tcp_sensors_socket = self.setup_tcp_client(self.remote_IP, self.tcp_sensors_port)
        
        """
        self.hyp_actuators_socket = threading.Thread(
            target=self.setup_tcp_client,
            args=(self.hyp_actuators_port))"""

        self.devices_udp = {}
        self.devices_tcp = {}

    def add_device(self, device_name, indexes, protocol, driver, types):
        values = get_type_values(driver, types, indexes)
        if not values:
            print(f'Device {device_name} not recognized')

        if len(values):
            if protocol == "opal-tcp":
                self.devices_tcp[device_name] = values
            elif protocol == "opal-udp":
                self.devices_udp[device_name] = values
            else:
                print("Protocol not recognized")
    
    def extract_sensors_data(self, device):
        data = []
        if "SM" in device:
            for sensor in self.devices_tcp[device][0]:
                if sensor == "lfP":
                    sensor = "Va"
                if sensor == "lfVolt":
                    sensor = "Vb"
                data.append(HyWorksApi.getLastSensorValues([f"{device}.{sensor}"])[0])
        return data
            

    ################### UDP SENSORS ########################
    def run_udp_sensors_socket(self):
        while True:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind(("0.0.0.0", self.hyp_udp_sensors_port))
            try:
                while True:
                    print(f"Waiting for data...{self.label}")
                    data, addr = sock.recvfrom(1024)
                    float_size = struct.calcsize('f')  # Size of one float in bytes
                    num_floats = len(data) // float_size

                    # Unpack the floats from the data
                    floats = struct.unpack('f' * num_floats, data)
                    packed_data = struct.pack('!' + 'f' * num_floats, *floats)

                    print(f"Received {num_floats} floats")
                    print(f"Floats: {floats}")

                    self.udp_sensors_socket.sendto(packed_data, (self.remote_IP, self.udp_sensors_port))
            except socket.timeout:
                print("Data wasn't received for 5 seconds")
            except KeyboardInterrupt:
                print(
                    '\nKeyboard interrupt detected. Closing socket..')
                sock.close()
                exit(0)
            except Exception as e:
                print(f"An error occurred in the edge {self.label} in port {self.hyp_udp_sensors_port}: {e}\n")
            finally:
                # Tanca el socket quan surtis del bucle                                                      
                sock.close()
                time.sleep(5)



    def setup_udp_client(self):
        # Configure the UDP socket (as client) for the delivery of the sensors data
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # No need to connect in UDP, just send data
        print(
            f'UDP socket ready to send data to 0.0.0.0:{self.udp_sensors_port} ({self.label})')
        return client_socket

    
    ################### TCP SENSORS ########################
    def run_tcp_sensors_socket(self):
        while True:
            while(True):
                try:
                    print(self.label)
                    for device in self.devices_tcp.keys():
                        print(device)
                        data = self.extract_sensors_data(device)
                        print("-----------------", data)
                        if len(data) == 0: continue
                        message_length = len(data)
                        print("-----------------", data)

                        # Prepare the message
                        sensors_data = struct.pack('!I', message_length)

                        for f_value in data:
                            sensors_data += struct.pack('!f', f_value) 

                        sensors_data += struct.pack('>h', ord('\n'))

                        self.tcp_sensors_socket.send(sensors_data)
                        print(f"Sending {sensors_data}...")
                        print(f"Sending to {self.label}...")

                    time.sleep(2)
                except Exception as e:
                    print(f"An error occurred in the edge {self.label} in port {self.tcp_sensors_port}: {e}\n")
                    print("closing")  
                    self.tcp_sensors_socket.close()
                time.sleep(2)                                                  
                    

    def send_data_tcp(self, data, socket):
        if socket:
            try:
                socket.sendall(data.encode())
                ip, port = socket.getpeername()
                print(f'Data sent to {ip}:{port}')
            except OSError as e:
                print(f'Error sending data: {e}')

    """
    ################### TCP ACTUATORS ######################
    def run_tcp_actuators_socket(self):
        socket = asnd("0.0.0.0", self.actuators_port)
        while(True):
            data = socket.receive()
            send_data_tcp(data, self.hyp_actuators_socket)
    """
    def setup_tcp_client(self, ip, port):
        # Create a TCP socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Attempt to connect to the remote server with retries every 3 seconds
        while True:
            try:
                client_socket.connect((ip, port))
                print(
                    f'Connected to {ip}:{port} ({self.label})')
                return client_socket
            except OSError as e:
                print(f'Connection error: {e}')
                print('Retrying in 3 seconds...')
                time.sleep(3)
                continue