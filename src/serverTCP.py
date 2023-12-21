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

#diccionari_nodes = get_json_data()[1]       #{"20001":["SM1"], "30001":["Ld5"]}

diccionari_nodes = {"31002": ["CB1"]}       # Ara mateix nomes es te en compte un node per edge (ex: {"20001":["SM1", "CB1"]} --> {"20001":["SM1"]})

def comunicate_to_hypersim(decoded_data, port, nom):
    # FIXME: aquesta linia inferior servirà quan li passi un -inf?
    for index, valor in enumerate(decoded_data):
        if valor != float('-inf'):
            if "SM" in nom: #Faltaria el cas del generador slack
                if index == 0:
                    print(f"canviant index {index}")
                    # HyWorksApi.setComponentParameter(nom, 'lfP', valor)           # Canviar agafant nomes ultima paraula de l'string nom
                elif index == 1:
                    # HyWorksApi.setComponentParameter(nom, 'lfVolt', valor)
                    print(f"canviant index {index}")
            elif "CB" in nom:
                if index == 0:
                    # HyWorksApi.setComponentParameter(nom, 'STATEa', valor)      #comprovar que a l'hypersim es fa aixi
                    print(f"canviant index {index}")
                elif index == 1:
                    # HyWorksApi.setComponentParameter(nom, 'STATEb', valor)
                    print(f"canviant index {index}")
                elif index == 2:
                    # HyWorksApi.setComponentParameter(nom, 'STATEc', valor)
                    print(f"canviant index {index}")
    print(f"Dades actualitzades en el {nom}")

def handle_client(client_socket, client_address, port, nom):
    try:
        while True:
            # length_bytes = client_socket.recv(4)
            # if not length_bytes:
            #     continue  # Sortir del bucle si no hi ha més dades
            # message_length = struct.unpack('>I', length_bytes)[0]
            # print(message_length)
            # Read the message containing the floats
            if "CB" in nom:
                message_length = 3
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
            comunicate_to_hypersim(received_floats, port, nom)
    except Exception as e:
        print(f"S'ha produït un error amb el client {client_address}: {e}")
    finally:
        # Tanca la connexió amb aquest client quan surtis del bucle
        client_socket.close()
        print(f"Connexió tancada amb {client_address}")


def receive_data(port, nom):
    host = 'localhost'  # Pots canviar-ho al teu IP si és remot
    while True:
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind((host, port))
            server_socket.listen()
            print(f"Servidor escoltant a {host}:{port}\n")
            # while True:
            client_socket, client_address = server_socket.accept()
            print(f"Connexió acceptada des de {client_address}, {nom}")
            handle_client(client_socket, client_address, port, nom)
        except Exception as e:
            print(f"S'ha produït un error en el port {port}: {e}\n")
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
    for clau, valor in diccionari_nodes.items(): # clau es el port, valor es el nom (SM1, Ld1...)
        threads[clau] = Thread(target=receive_data, args=(int(clau), valor[0]))

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