import json
import os
import sys
import struct
import time
import socket
import threading

class Edge():
    def __init__(self, label, sensor_port, actuator_port, devices):
        self.label = label
        self.local_IP = 'localhost'
        self.remote_IP = 'localhost'
        self.sensor_port_remote = int(sensor_port)
        self.sensor_port_local = int(sensor_port) - 1
        self.actuator_port = int(actuator_port)
        self.devices = devices
        self.sensor_socket = None
        self.actuator_socket = None
    
    def add_device(self, device_name, indexs):
        if 'SM' in device_name.split()[-1] and len(indexs) == 2:
            self.devices[device_name] = (['lfP', 'lfVolt'], indexs)     # Falta el cas del generador Slack
            print(self.devices[device_name])
        elif 'Ld' in device_name.split()[-1] and len(indexs) == 2:
            self.devices[device_name] = (['Po', 'Qo'], indexs)
        elif 'CB' in device_name.split()[-1] and len(indexs) == 3:
            self.devices[device_name] = (['STATEa', 'STATEb', 'STATEc'], indexs)
        else:
            print(f"Device {device_name} not recognized")

    def run_send_sensors_data(self):
        # Format and send the sensors data to the Edge
        while True:
            self.check_and_reconnect_sensors_coms()     # Check the connection

            sensors_data = b''
            data_list = self.extract_sensors_data()   # Get the data from Hypersim
            
            values = []
            for i in data_list:
                values.append(i)
            message_length = len(values)

            # Prepare the message
            sensors_data = struct.pack('!I', message_length)

            for f_value in data_list:
                sensors_data += struct.pack('!f', f_value) 

            sensors_data += struct.pack('>h', ord('\n'))

            if self.sensor_socket is None:
                print("The socket is not configured")
            else:
                try:
                    self.sensor_socket.send(sensors_data)
                    print(f"Sending {sensors_data}...")
                    print(f"Sending to {self.label}...")
    
                except OSError as e:
                    print(f"Error sending data to {self.label}: {e}")
                    self.sensor_socket = None
            
            time.sleep(5)

    def setup_sensors_port(self):
        # Configure the TCP socket (as client) for the delivery of the sensors data to the TCP server in the corresponding Edge
        self.sensor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sensor_socket.bind((self.local_IP, self.sensor_port_local))
        self.sensor_socket.settimeout(5)
        try:
            # Try to connect to the Edge server
            self.sensor_socket.connect((self.remote_IP, self.sensor_port_remote))
            print(f'Connecting to {self.remote_IP} through port {self.sensor_port_remote} ({self.label})')
        except OSError as e:
            print(f'Connection error: {e}')
            self.sensor_socket = None

    def check_and_reconnect_sensors_coms(self):
        # Check the connection to the TCP server and reconnect in case of failure
        while True:
            try:
                if self.sensor_socket is not None:
                    pass
                else:
                    self.setup_sensors_port()
            except OSError as e:
                print(f'Error en la connexió {self.label}: {e}')
                self.sensor_socket = None
                # Wait before attempting the connection again.
                print(f'Waiting before attempting the connection again to {self.label}...')
                time.sleep(5)
                continue
            break  # Connection succesfull, exit the loop

    def extract_sensors_data(self):
        # Extract the sensors data from the Hypersim software using the HyWorksApi library
        dades = []
        order = 0
        pending_devices = []
        try:
            for dev_name in self.devices:
                if 'CB' in dev_name:
                    for sensor in self.devices[dev_name][0]:
                        if order in self.devices[dev_name][1]:
                            dades.append(HyWorksApi.getLastSensorValues([dev_name.split()[-1] + '.' + sensor])[0])
                            order = order + 1
                        else:
                            pending_devices.append(dev_name)
                            break
                else:
                    for sensor in self.devices[dev_name][0]:
                        if order in self.devices[dev_name][1]:
                            dades.append(HyWorksApi.getComponentParameter(dev_name.split()[-1], sensor)[0])
                            order = order + 1
                        else:
                            pending_devices.append(dev_name)
            # In case of disordered devices this loop is executed (only works for 2 devices/edge)
            if pending_devices != []:
                for dev_name in pending_devices:
                    if 'CB' in dev_name:
                        for sensor in self.devices[dev_name][0]:
                            if order in self.devices[dev_name][1]:
                                dades.append(HyWorksApi.getLastSensorValues([dev_name.split()[-1] + '.' + sensor])[0])
                                order = order + 1
                    else:
                        for sensor in self.devices[dev_name][0]:
                            if order in self.devices[dev_name][1]:
                                dades.append(HyWorksApi.getComponentParameter(dev_name.split()[-1], sensor)[0])
                                order = order + 1
        except Exception:
            print('error with device: ' + self.label)
        return dades

    def run_receive_actuators_data(self):
        # Receive and decode the actuators data
        try:
            while True:
                self.check_and_reconnect_actuators_coms()

                message_length = max(max(values[1]) for values in self.devices.values()) + 1

                message_bytes = self.actuator_socket.recv(message_length*4)

                # Process the message bytes containing the floats
                number_of_floats = message_length  # Assuming 4 bytes per float
                received_floats = struct.unpack('!' + 'f' * number_of_floats, message_bytes)
                # Handle the received floats
                print("Received", len(received_floats), "floats:")
                for f in received_floats:
                    print(f)

                # Read the end-of-line character to indicate the end of the message
                # eol = client_socket.recv(1)
                # print(eol)
                # if eol != b'\n':
                #     print("Invalid end-of-line character")
                #     continue
                self.insert_actuators_data(received_floats)
        except Exception as e:
            print(f"S'ha produït un error amb el client {self.actuator_port}: {e}")
        finally:
            # Tanca la connexió amb aquest client quan surtis del bucle
            self.actuator_socket.close()
            print(f"Connexió tancada amb {self.actuator_port}")

    def setup_actuators_port(self):
            # Configure the TCP socket (as server) for the reception of the actuators data from the TCP client in the corresponding Edge
            try:
                self.actuator_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.actuator_socket.bind((self.local_IP, self.actuator_port))
                self.actuator_socket.listen()
                print(f"Servidor escoltant a {self.local_IP}:{self.actuator_port}\n")

                client_socket, client_address = self.actuator_socket.accept()
                print(f"Connexió acceptada des de {client_address}, {self.label}")

            except Exception as e:
                print(f"S'ha produït un error en el port {self.actuator_port}: {e}\n")

    def check_and_reconnect_actuators_coms(self):
        # Reconnect to the TCP client in case of failure
        while True:
            try:
                if self.actuator_socket is not None:
                    pass
                else:
                    self.setup_actuators_port()
            except OSError as e:
                print(f'Connection Error on {self.label}: {e}')
                self.actuator_socket = None
                # Wait before attempting the connection again.
                print(f'Waiting before attempting the connection again to {self.label}...')
                time.sleep(5)
                continue
            break  # Connection succesfull, exit the loop

    def insert_actuators_data(self, decoded_data):
        # Input the actuators data to the Hypersim model using the HyWorksApi library
        i = 0
        for dev_name in self.devices:
            for sensor in self.devices[dev_name][0]:
                if decoded_data[i] != float('-inf'):
                    print(f"canviant sensor {sensor} del dispositiu {dev_name} de l'edge {self.label}")
                    HyWorksApi.setComponentParameter(dev_name.split()[-1], sensor, decoded_data[i])
                i = i+1    

        print(f"Dades actualitzades en el {self.label}")


def get_json_data():
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # Crear la ruta al fitxer JSON a partir de la ruta de l'script

    ruta_fitxers = os.path.join(current_directory, '../setup/')
    i = 0
    edge_list = []
    # d_sensors = {}
    # d_actuators = {}
    for file in os.listdir(ruta_fitxers):
        adr_edge = os.path.join(ruta_fitxers, file)
        if i == 2:
            break
        with open(adr_edge, 'r') as file:
            # Llegir el contingut del fitxer
            data = json.load(file)
            edge_name = data['global-properties']['label']
            sensors_port = data['global-properties']['comms']['opal-tcp']['sensors']['port']
            actuadors_port = data['global-properties']['comms']['opal-tcp']['actuators']['port']
            devices = {}
            objecte_edge = Edge(edge_name, sensors_port, actuadors_port, devices)
            for device in data['devices']:
                if device['properties']['comm-type'] == 'opal-tcp':
                    device_name = device['label']
                    indexes = device['properties']['indexes']
                    objecte_edge.add_device(device_name, indexes)
            edge_list.append(objecte_edge)
        i = i + 1

    return(edge_list)

def hypersim_setup():
    hypersimDir = r"C:\\OPAL-RT\\HYPERSIM\\hypersim_2023.2.1.o404"
    if not os.path.isdir(hypersimDir):
        print("INVALID HYPERSIM DIRECTORY SPECIFIED IN THE SCRIPT")
        exit(1)
    sys.path.append(os.path.join(hypersimDir, 'Windows', 'HyApi', 'python'))
    import HyWorksApiGRPC as HyWorksApi
    HyWorksApi.startAndConnectHypersim()
    print(os.path.realpath(__file__))
    designPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'HVAC_230kV_9Bus_IEEE.ecf')
    print(designPath)
    HyWorksApi.openDesign(designPath)

def main():
    # hypersim_setup()
    edge_list = get_json_data()
    threads = []
    for edge in edge_list:
        print(edge.devices)
        thread_sensor = threading.Thread(target=edge.run_send_sensors_data, args=())
        thread_actuator = threading.Thread(target=edge.run_receive_actuators_data, args=())
        thread_sensor.start()
        thread_actuator.start()
        threads.append(thread_sensor)
        threads.append(thread_actuator)

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()