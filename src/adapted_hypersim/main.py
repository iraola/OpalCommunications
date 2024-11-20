"""
This class is in charge of running the sockets, which are bridges between the
edges and the Opal. These sockets can use tcp (actuators and some sensors) or
udp (sensors) protocols.

Usage: python adapted_hypersim.py [protocol]
Supported protocols = "udp"/"tcp"
Default: protocol = "udp"
"""

import os
import json
import sys
import threading

from Edge import Edge
from utils import hypersim_setup


def main(protocol):
    edge_list = get_json_data()
    hypersim_setup()

    if protocol != "udp" and protocol != "tcp":
        raise Exception("Protocol must be udp or tcp")

    threads = []
    for edge in edge_list:
        if protocol == "udp":
            t1 = threading.Thread(target=edge.run_udp_sensors_socket, args=())
            t1.start()
            threads.append(t1)
        else:
            t2 = threading.Thread(target=edge.run_tcp_sensors_socket, args=())
            t3 = threading.Thread(target=edge.run_tcp_actuators_socket, args=())
            t2.start()
            t3.start()
            threads.append(t2)
            threads.append(t3)

    for t in threads:
        t.join()

def get_json_data():
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # Crear la ruta al fitxer JSON a partir de la ruta de l'script

    ruta_fitxers = os.path.join(current_directory, '//wsl.localhost/Ubuntu/home/ubuntu/hp2cdt/deployments/9-buses-hypersim/setup')
    edge_list = []
    # d_sensors = {}
    # d_actuators = {}
    with open(os.path.join(current_directory, "types.json")) as file:
        types = json.load(file)

    for file in os.listdir(ruta_fitxers):
        adr_edge = os.path.join(ruta_fitxers, file)
        with open(adr_edge, 'r') as file:
            # Llegir el contingut del fitxer
            data = json.load(file)
            edge_name = data['global-properties']['label']
            tcp_sensors_port = data['global-properties']['comms']['opal-tcp']['sensors']['port']
            udp_sensors_port = data['global-properties']['comms']['opal-udp']['sensors']['port']
            actuadors_port = data['global-properties']['comms']['opal-tcp']['actuators']['port']
            objecte_edge = Edge(edge_name, tcp_sensors_port, udp_sensors_port, actuadors_port)

            for device in data['devices']:
                device_name = device['label']
                driver = device['driver']
                indexes = device['properties']['indexes']
                protocol = device['properties']['comm-type']
                objecte_edge.add_device(device_name, indexes, protocol, driver, types)
            edge_list.append(objecte_edge)

    return edge_list


if __name__ == "__main__":
    if len(sys.argv) < 2:
        protocol = "udp"
    else:
        protocol = sys.argv[1]
    main(protocol)