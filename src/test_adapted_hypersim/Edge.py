import os
import socket
import struct
import sys
import threading
import time

from utils import get_type_values, get_last_int

hypersimDir = r"C:\\OPAL-RT\\HYPERSIM\\hypersim_2024.1.0.o39"
if not os.path.isdir(hypersimDir):
    print("INVALID HYPERSIM DIRECTORY SPECIFIED IN THE SCRIPT")
    exit(1)
sys.path.append(os.path.join(hypersimDir, 'Windows', 'HyApi', 'python'))
import HyWorksApiGRPC as HyWorksApi

lock = threading.Lock()

class Edge():
    def __init__(self, label, tcp_sensors_port, udp_sensors_port,
                 actuator_port):
        self.label = label
        self.local_IP = '0.0.0.0'#'10.64.117.60'
        self.remote_IP = '172.31.144.1'

        self.hyp_udp_sensors_port = int(udp_sensors_port) + 2
        self.hyp_tcp_sensors_port = int(tcp_sensors_port) + 2
        self.hyp_actuators_port = int(actuator_port) + 2
        self.udp_sensors_port = int(udp_sensors_port)
        self.tcp_sensors_port = int(tcp_sensors_port)
        self.tcp_actuators_port = int(actuator_port)

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

    def get_sensors_data(self, device):
        data = []
        for sensor in self.devices_tcp[device][0]:
            if "CB" in device:
                with lock:
                    d = HyWorksApi.getLastSensorValues([f"{device}.{sensor}"])
            else:
                with lock:
                    d = HyWorksApi.getComponentParameter(device, sensor)
            if len(d) > 0:
                data.append(float(d[0]))
            else: data.append(float('-inf'))
        return data

    def set_sensors_data(self, decoded_data):
        # Input the actuators data to the Hypersim model using the HyWorksApi library
        i = 0
        modified = False
        for dev_name in self.devices_tcp:
            cb_value = -1
            sensors_names = self.devices_tcp[dev_name][0]
            for sensor in sensors_names:
                if decoded_data[i] != float('-inf'):
                    modified = True
                    print(
                        f"Setting value {sensor} from device {dev_name}, edge {self.label}")
                    if "CB" in dev_name:
                        if cb_value == -1:
                            cb_value = 0
                        cb_value += decoded_data[i] * pow(2, i)
                    else:
                        with lock:
                            HyWorksApi.setComponentParameter(dev_name,
                                                            sensor, decoded_data[i])
                i = i + 1
            if cb_value != -1:
                if "CB" in dev_name:
                    last_int = get_last_int(dev_name)
                    with lock:
                        HyWorksApi.setComponentParameter(f"Const{last_int}",
                                                        "K", int(cb_value))

        if modified: print(f"Data updated in {self.label}")


    ################### UDP SENSORS ########################
    def run_udp_sensors_socket(self):
        while True:
            udp_sensors_socket = self.setup_udp_client()  # TODO: check multiprocessing

            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind((self.local_IP, self.hyp_udp_sensors_port))
            try:
                while True:
                    print(f"Waiting for data...{self.label}")
                    data, addr = sock.recvfrom(1024)
                    float_size = struct.calcsize(
                        'f')  # Size of one float in bytes
                    num_floats = len(data) // float_size

                    # Unpack the floats from the data
                    floats = struct.unpack('f' * num_floats, data)
                    packed_data = struct.pack('!' + 'f' * num_floats, *floats)

                    print(f"Received {num_floats} floats")
                    print(f"Floats: {floats}")

                    udp_sensors_socket.sendto(packed_data, (
                    self.remote_IP, self.udp_sensors_port))
            except socket.timeout:
                print("Data wasn't received for 5 seconds")
            except KeyboardInterrupt:
                print(
                    '\nKeyboard interrupt detected. Closing socket..')
                sock.close()
                udp_sensors_socket.close()
                exit(0)
            except Exception as e:
                print(
                    f"An error occurred in the edge {self.label} in port {self.hyp_udp_sensors_port}: {e}\n")
            finally:
                # Tanca el socket quan surtis del bucle
                sock.close()
                udp_sensors_socket.close()
                time.sleep(5)

    def setup_udp_client(self):
        # Configure the UDP socket (as client) for the delivery of the sensors data
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # No need to connect in UDP, just send data
        print(
            f'UDP socket ready to send data to {self.local_IP}:{self.udp_sensors_port} ({self.label})')
        return client_socket


    ################### TCP SENSORS ########################
    def run_tcp_sensors_socket(self):
        while True:
            tcp_sensors_socket = self.setup_tcp_client(self.remote_IP,
                                                       self.tcp_sensors_port)
            while (True):
                try:
                    data = []
                    for device in self.devices_tcp.keys():
                        print(device)
                        data.extend(self.get_sensors_data(device))

                    if len(data) == 0: continue
                    message_length = len(data)

                    # Prepare the message
                    sensors_data = struct.pack('!I', message_length)

                    for f_value in data:
                        sensors_data += struct.pack('!f', f_value)

                    sensors_data += struct.pack('>h', ord('\n'))

                    tcp_sensors_socket.send(sensors_data)
                    print(f"Sending {sensors_data}...")
                    print(f"Sending to {self.label}...")

                except Exception as e:
                    print(
                        f"An error occurred in the edge {self.label} in port {self.tcp_sensors_port}: {e}\n")
                    print("closing")
                    tcp_sensors_socket.close()
                time.sleep(10)


    ################### TCP ACTUATORS ######################
    def run_tcp_actuators_socket(self):
        while True:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind((self.local_IP, self.tcp_actuators_port))
            sock.listen()
            print(
                f"Server listening at {self.local_IP}:{self.tcp_actuators_port}\n")

            conn, address = sock.accept()
            print(f"Accepted connexion from {address}, {self.label}")
            try:
                while True:
                    message_length = max(max(values[1]) for values in
                                         self.devices_tcp.values()) + 1
                    print("Message length: ", message_length)

                    # Receive the integer containing the length of the message
                    length_bytes = conn.recv(4)
                    message_length_received = \
                        struct.unpack('!I', length_bytes)[0]
                    if message_length_received != message_length:
                        print(
                            "Expected length doesn't match with received length",
                            file=sys.stderr)

                    # Receive message (Float * message_length)
                    message_bytes = conn.recv(message_length * 4)
                    received_floats = struct.unpack('!' + 'f' * message_length,
                                                    message_bytes)

                    # Receive new line character
                    newline_bytes = conn.recv(2)
                    newline_character = struct.unpack('>h', newline_bytes)[0]
                    if chr(newline_character) != '\n':
                        print("New line not found at the end of the message.",
                              file=sys.stderr)

                    for f in received_floats:
                        print(f)

                    self.set_sensors_data(received_floats)

            except Exception as e:
                print(
                    f"There was an error with client {self.tcp_actuators_port}: {e}")
                sock.close()

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
