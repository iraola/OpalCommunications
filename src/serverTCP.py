import socket
from threading import Thread
import time
import struct
from read_json import get_json_data

# TODO: Utilitzar aquesta funcio quan em connecti a Hypersim
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

data_dict = {'DE1': '', 'DE2': '', 'DE3': '', 'DE16': '', 'DE17': '', 'DE18': ''}
exit_flag = False


#Llegir fitxers json i crear els objectes
classes_edge = get_json_data()

def comunicate_to_hypersim(decoded_data, edge):
    i = 0
    for dispositiu in edge.devices:
        for sensor in edge.devices[dispositiu]:
            if decoded_data[i] != float('-inf'):
                print(f"canviant sensor {sensor} del dispositiu {dispositiu} de l'edge {edge.label}")
                HyWorksApi.setComponentParameter(dispositiu.split()[-1], sensor, decoded_data[i])
            i = i+1    

    print(f"Dades actualitzades en el {edge.label}")

def handle_client(client_socket, edge):
    try:
        while True:

            message_length = max(max(indices) for indices in edge.devices.values()) + 1

            message_bytes = client_socket.recv(message_length*4)
            # print(message_bytes)
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
            comunicate_to_hypersim(received_floats, edge)
    except Exception as e:
        print(f"S'ha produït un error amb el client {edge.actuator_port}: {e}")
    finally:
        # Tanca la connexió amb aquest client quan surtis del bucle
        client_socket.close()
        print(f"Connexió tancada amb {edge.actuator_port}")


def receive_data(edge):
    host = 'localhost'  # Pots canviar-ho al teu IP si és remot
    while True:
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind((host, edge.actuator_port))
            server_socket.listen()
            print(f"Servidor escoltant a {host}:{edge.actuator_port}\n")
            # while True:
            client_socket, client_address = server_socket.accept()
            print(f"Connexió acceptada des de {client_address}, {edge.nom_edge}")
            # handle_client(client_socket, client_address, edge.actuator_port, edge.nom_edge)
            handle_client(client_socket, edge)
        except Exception as e:
            print(f"S'ha produït un error en el port {edge.actuator_port}: {e}\n")
        finally:
            # Tanca el socket quan surtis del bucle
            server_socket.close()
            time.sleep(5)

def main():
    # TODO: Utilitzar aquesta funcio quan vulgui connectarme a Hypersim.
    # Cridem la funció per utilitzar la API de Hypersim
    """setup_inicial()"""

    global exit_flag
    threads = {}
    for edge in classes_edge: 
        threads[edge.nom_edge] = Thread(target=receive_data, args=(edge,))

    # Inicia els fils
    for thread in threads.values():
        thread.start()

    try:
        # Espera que tots els fils finalitzin
        for thread in threads.values():
            thread.join()
        
    except KeyboardInterrupt:
        exit_flag=True
        print("Interrupció de l'usuari. Esperant que els fils finalitzin...")

    # Imprimeix el diccionari amb les dades
    print("Diccionari de dades associades als ports:")
    print(data_dict)



if __name__ == "__main__":
    main()

"""Vull implementar que:
0. Que els threads, en lloc d'emmagatzemar-se en una llista ho facin en un diccionari. """"""
1. Les primeres dades rebudes es guardin en un diccionari on les claus seran les mateixes que les dels threads,
de manera que poguem emmagatzemar la info que arriba a cada thread en aquell diccionari.""""""
1.1. Investigar per quin motiu salta l'error settimeout quan executo el codi que tinc escrit fins el momnet.""""""
2. A partir del segon cop que es reben dades, que es comparin amb les que hi podem trobar en el diccionar i es 
substitueixi el valor antic pel nou, si ha canviat.""""""
3. Que s'envii quan el valor ha canviat (en un pas posterior, afegir que s'actualitzi a hypersim en aquest 
mateix moment)
4. Afegir funcio de calcular la dada que s'ha d'actualitzar a hypersim
5. Hauria d'afegir alguna part que fes que cada 5 segons tots els threads es trobin en el mateix punt (enviament o check i reconnect...)"""