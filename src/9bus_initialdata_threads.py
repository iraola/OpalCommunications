import struct
import time
from socketTCP import socketTCP
import threading
from read_json import get_json_data

# FIXME: utilitzar aquesta part quan vulgui utilitzar el programa amb hypersim
# Funcio per poder-nos connectar a Hipersim
"""
def setup_inicial():
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
    HyWorksApi.openDesign(designPath)"""

# TODO: Descomentar aquesta part quan connecti el programa a Hypersim.
# Executem la funcio per utilitzar la API de Hypersim
"""setup_inicial()"""

# Crear instàncies de socketTCP
print("Les dades seran enviades a través dels següents ports:\n")
objectes_socket_tcp = {}


#Llegir fitxers json i crear els objectes
# Ara mateix nomes es te en compte un node per edge (ex: {"20001":["SM1", "CB1"]} --> {"20001":["SM1"]})
'''
diccionari_nodes = get_json_data()[0]       #{"20001":["SM1"], "30001":["Ld5"]}
for clau, valor in diccionari_nodes.items():
    if valor != []:
        objecte = socketTCP(clau, valor)
        objectes_socket_tcp[clau] = objecte
        print(f"Clau: {clau}, Port Server: {objecte.portServer}, Port Client: {objecte.portClient}")
'''
        

classes_edge = get_json_data()
for edge in classes_edge:
    if edge.devices != {}:
        objecte = socketTCP(edge.edge_name, edge.sensor_port, edge.devices)
        objectes_socket_tcp[edge.edge_name] = objecte
        print(f"Clau: {objecte.nom_edge}, Port Server: {objecte.portServer}, Port Client: {objecte.portClient}")


#objecte = socketTCP("11002", ["CB1"])
#objectes_socket_tcp["11002"] = objecte


# Funció per aplicar threading a l'enviament de dades
def enviar_dades_thread(objecte):
    while True:
        message = b''
        objecte.check_and_reconnect()
        data_list = actualitzar_dades(objecte)   #Funcio per llegir noves dades d'Hypersim
        
        # objecte.enviar_dades_tcp(struct.pack('!I', len(dades_a_enviar)))
        # objecte.enviar_dades_tcp(dades_a_enviar)
        # objecte.enviar_dades_tcp(b'\n')
        values = []
        for i in data_list:
            values.append(i)
        message_length = len(values)

        # Preparar el mensaje
        message = struct.pack('!I', message_length)
        # message += struct.pack(f">{message_length}f", *values)
        for f_value in data_list:
            message += struct.pack('!f', f_value) 
        # message += b'\n'        
        # message += struct.pack('!p', b'\n')
        message += struct.pack('>h', ord('\n'))

        objecte.enviar_dades_tcp(message)

        time.sleep(5)


# Diccionari per fer proves d'enviament de dades.
# Serà substituit per les dades exretes d'hypersim.
# data_dict = {'DE1': ['1.04', '1.0', '0.0', '1.0', '7.0'], 'DE2': ['163000000', '1.025'], 
#     'DE3': ['85000000', '1.025'], 'DE4': ['125000000', '50000000'], 
#     'DE5': ['90000000', '30000000'], 'DE6': ['100000000', '35000000'], 
#     'DE16': [1.0, 1.0, 1.0], 'DE17': [1.0, 1.0, 1.0], 'DE18': [1.0, 1.0, 1.0]}

# FIXME: utilitzar aquesta part quan vulgui utilitzar el programa amb hypersim
# Diccionari que utilitzarem quan estiguem fent servir Hypersim, per extreure les dades de la simulacio.

def actualitzar_dades(objecte):
    dades = []
    try:
        for dispositiu in objecte.devices:
            if 'CB' in dispositiu:
                for sensor in objecte.devices[dispositiu]:
                    dades.append(HyWorksApi.getLastSensorValues([dispositiu.split()[-1] + '.' + sensor])[0])
            else:
                for sensor in objecte.devices[dispositiu]:
                    dades.append(HyWorksApi.getComponentParameter(dispositiu.split()[-1], sensor)[0])
    except Exception:
        print('error with device: ' + objecte.nom_edge)
    return dades


# TODO: Començo un thread que sigui un while True, que vagi recarregant el diccionari?
# Iniciem els threads d'enviament pels diferents sockets que hem creat
threads = []
for clau, objecte in objectes_socket_tcp.items():
    thread = threading.Thread(target=enviar_dades_thread, args=(objecte,))
    thread.start()
    threads.append(thread)

# TODO: Cal que busqui alguna manera per ajuntar els threads al llarg de l'execució?
# Esperar que tots els fils finalitzin
""" Afegir un punt d'unio dels diferents threads al llarg de l'enviament?"""
for thread in threads:
    thread.join()
