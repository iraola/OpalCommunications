import json
import os

def get_json_data():
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # Crear la ruta al fitxer JSON a partir de la ruta de l'script

    ruta_fitxers = os.path.join(current_directory, '../setup/9-buses/')
    i = 0
    d_sensors = {}
    d_actuators = {}
    for file in os.listdir(ruta_fitxers):
        adr_edge = os.path.join(ruta_fitxers, file)
        if i == 2:
            break
        with open(adr_edge, 'r') as file:
            # Llegir el contingut del fitxer
            data = json.load(file)
            sensors_port = data['global-properties']['comms']['opal-tcp']['sensors']['port']
            actuadors_port = data['global-properties']['comms']['opal-tcp']['actuators']['port']
            for device in data['devices']:
                if device['properties']['comm-type'] == 'opal-tcp':
                    device_name = device['label']
                    d_sensors.update({sensors_port: [device_name]})
                    d_actuators.update({actuadors_port: [device_name]})
                    break
        i = i + 1

    return(d_sensors, d_actuators)
