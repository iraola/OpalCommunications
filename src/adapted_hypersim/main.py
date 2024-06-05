import os
import json

from src.adapted_hypersim.Edge import Edge


def main():
    edge_list = get_json_data()
    for edge in edge_list:
        edge.run_udp_sensors_socket()
        #edge.run_tcp_sensors_socket()
        #edge.run_tcp_actuators_socket()


def get_json_data():
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # Crear la ruta al fitxer JSON a partir de la ruta de l'script

    ruta_fitxers = os.path.join(current_directory, '../../setup-9-buses/')
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
    main()