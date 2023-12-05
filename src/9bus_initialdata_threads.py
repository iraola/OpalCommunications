import struct
import time
from socketTCP import socketTCP
import threading

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

#Creem tots els objectes de la classe socketTCP amb el diccionari i el bucle seguent
# Diccionari de tuples: (M, CD, TCP)
diccionariDE = {'DE1': (1, 1, 1), 'DE2': (1, 2, 1), 'DE3': (1, 3, 1), 'DE4': (2, 5, 1), 'DE5': (2, 6, 1),
                'DE6': (2, 8, 1), 'DE7': (3, 4, 0), 'DE8': (3, 7, 0), 'DE9': (3, 9, 0), 'DE10': (4, 1, 0),
                'DE11': (4, 2, 0), 'DE12': (4, 3, 0), 'DE13': (4, 4, 0), 'DE14': (4, 5, 0), 'DE15': (4, 6, 0),
                'DE16': (5, 1, 1), 'DE17': (5, 2, 1), 'DE18': (5, 3, 1)}
# Crear instàncies de socketTCP
print("Les dades seran enviades a través dels següents ports:\n")
objectes_socket_tcp = {}

"""for clau, valor in diccionariDE.items():
    if valor[2] == 1:
        M, CD, _ = valor
        objecte = socketTCP(M, CD, clau)
        objectes_socket_tcp[clau] = objecte
        print(f"Clau: {clau}, Port Server: {objecte.portServer}, Port Client: {objecte.portClient}")"""

objecte = socketTCP(0,0,"DE1")
objectes_socket_tcp["DE1"] = objecte


# Funció per aplicar threading a l'enviament de dades
def enviar_dades_thread(objecte, data_dict):
    dades_a_enviar = b''
    while True:
        objecte.check_and_reconnect()
        if objecte.nom in data_dict:
            #dades_a_enviar = ','.join(map(str, data_dict[objecte.nom]))
            # dades_a_enviar = data_dict[obj]
            for f_value in data_dict[objecte.nom]:
                dades_a_enviar += struct.pack('f', float(f_value))
            objecte.enviar_dades_tcp(struct.pack('!I', len(dades_a_enviar)))
            objecte.enviar_dades_tcp(dades_a_enviar)
            objecte.enviar_dades_tcp(b'\n')


# Diccionari per fer proves d'enviament de dades.
# Serà substituit per les dades exretes d'hypersim.
data_dict = {'DE1': ['1.04', '1.0', '0.0', '1.0', '7.0'], 'DE2': ['163000000', '1.025'], 
    'DE3': ['85000000', '1.025'], 'DE4': ['125000000', '50000000'], 
    'DE5': ['90000000', '30000000'], 'DE6': ['100000000', '35000000'], 
    'DE16': [1.0, 1.0, 1.0], 'DE17': [1.0, 1.0, 1.0], 'DE18': [1.0, 1.0, 1.0]}

# FIXME: utilitzar aquesta part quan vulgui utilitzar el programa amb hypersim
# Diccionari que utilitzarem quan estiguem fent servir Hypersim, per extreure les dades de la simulacio.
"""
# Extraiem les dades del model
data_dict = {}
# generadors
data_dict['SM1'] = [HyWorksApi.getComponentParameter('SM1', 'lfVolt')[0], '']
data_dict['SM2'] = [HyWorksApi.getComponentParameter('SM2', 'lfP')[0],
                    HyWorksApi.getComponentParameter('SM2', 'lfVolt')[0]]
data_dict['SM3'] = [HyWorksApi.getComponentParameter('SM3', 'lfP')[0],
                    HyWorksApi.getComponentParameter('SM3', 'lfVolt')[0]]
# carregues
data_dict['DE4'] = [HyWorksApi.getComponentParameter('Ld5', 'Po')[0], HyWorksApi.getComponentParameter('Ld5', 'Qo')[0]]
data_dict['DE5'] = [HyWorksApi.getComponentParameter('Ld6', 'Po')[0], HyWorksApi.getComponentParameter('Ld6', 'Qo')[0]]
data_dict['DE6'] = [HyWorksApi.getComponentParameter('Ld8', 'Po')[0], HyWorksApi.getComponentParameter('Ld8', 'Qo')[0]]
# interruptors
data_dict['DE16'] = [HyWorksApi.getLastSensorValues(['CB1.STATEa'])[0],
                     HyWorksApi.getLastSensorValues(['CB1.STATEb'])[0],
                     HyWorksApi.getLastSensorValues(['CB1.STATEc'])[0]]
data_dict['DE17'] = [HyWorksApi.getLastSensorValues(['CB2.STATEa'])[0],
                     HyWorksApi.getLastSensorValues(['CB2.STATEb'])[0],
                     HyWorksApi.getLastSensorValues(['CB2.STATEc'])[0]]
data_dict['DE18'] = [HyWorksApi.getLastSensorValues(['CB3.STATEa'])[0],
                     HyWorksApi.getLastSensorValues(['CB3.STATEb'])[0],
                     HyWorksApi.getLastSensorValues(['CB3.STATEc'])[0]]"""

# TODO: Començo un thread que sigui un while True, que vagi recarregant el diccionari?
# Iniciem els threads d'enviament pels diferents sockets que hem creat
threads = []
for clau, objecte in objectes_socket_tcp.items():
    thread = threading.Thread(target=enviar_dades_thread, args=(objecte, data_dict))
    thread.start()
    threads.append(thread)

# TODO: Cal que busqui alguna manera per ajuntar els threads al llarg de l'execució?
# Esperar que tots els fils finalitzin
""" Afegir un punt d'unio dels diferents threads al llarg de l'enviament?"""
for thread in threads:
    thread.join()
