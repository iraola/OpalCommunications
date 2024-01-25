import json
import os

class Edge():
    def __init__(self, label, sensor_port, actuator_port, devices):
        self.label = label
        self.sensor_port = sensor_port
        self.actuator_port = actuator_port
        self.devices = devices
    
    def afegir_device(self, nom_device, indexs):
        if 'SM' in nom_device.split()[-1] and len(indexs) == 2:
            self.devices[nom_device] = ['lfP', 'lfVolt']     # Falta el cas del generador Slack
        elif 'Ld' in nom_device.split()[-1] and len(indexs) == 2:
            self.devices[nom_device] = ['Po', 'Qo']
        elif 'CB' in nom_device.split()[-1] and len(indexs) == 3:
            self.devices[nom_device] = ['STATEa', 'STATEb', 'STATEc']   
                
def get_json_data():
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # Crear la ruta al fitxer JSON a partir de la ruta de l'script

    ruta_fitxers = os.path.join(current_directory, '../setup/')
    i = 0
    llista_obj = []
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
                    device_name = device['label'] # Agafar nomes ultima paraula
                    indexes = device['properties']['indexes']
                    objecte_edge.afegir_device(device_name, indexes)
                    # d_sensors.update({sensors_port: [device_name]})
                    # d_actuators.update({actuadors_port: [device_name]})
            llista_obj.append(objecte_edge)
        i = i + 1

    return(llista_obj)

llista = get_json_data()
print(llista)
for l in llista:
    print(l.devices)