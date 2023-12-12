import json
import os

def get_json_data():
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # Crear la ruta al fitxer JSON a partir de la ruta de l'script

    ruta_fitxers = os.path.join(current_directory, '../setup/9-buses/')

    sensors = {}
    actuadors = {}

    for file in os.listdir(ruta_fitxers):
        adr_edge = os.path.join(ruta_fitxers, file)
        with open(adr_edge, 'r') as file:
            # Llegir el contingut del fitxer
            data = json.load(file)
            sensors.update(data['global-properties']['comms']['tcp-sensors']['ports'])
            actuadors.update(data['global-properties']['comms']['tcp-actuators']['ports'])

    return(sensors, actuadors)
