import socket
from threading import Thread
import time

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

def nom_dispositiu_edge(port):
    dispositius = {
        21014: 'DE1',
        21024: 'DE2',
        21034: 'DE3',
        25014: 'DE16',
        25024: 'DE17',
        25034: 'DE18'
    }
    return(dispositius.get(port))

diccionari_components = {'DE1_0': ('DE1', 'lfVolt'),
'DE2_0': ('DE2', 'lfP'), 'DE2_1': ('DE2', 'lfVolt'),
'DE3_0': ('DE3', 'lfP'), 'DE3_1': ('DE3', 'lfVolt'),
'DE16_0': ('DE16', 'STATEa'), 'DE16_1': ('DE16', 'STATEb'), 'DE16_2': ('DE16', 'STATEc'),
'DE17_0': ('DE17', 'STATEa'), 'DE17_1': ('DE17', 'STATEb'), 'DE17_2': ('DE17', 'STATEc'),
'DE18_0': ('DE18', 'STATEa'), 'DE18_1': ('DE18', 'STATEb'), 'DE18_2': ('DE18', 'STATEc')}
def comunicate_to_hypersim(decoded_data, port):
    DE = nom_dispositiu_edge(port)
    data_dict[nom_dispositiu_edge(port)] = decoded_data
    # passar a info rebuda a llista
    llista_data = decoded_data.split(',')
    #passar elements a floats
    # FIXME: aquesta linia inferior servirà quan li passi un -inf?
    llista_data = [float(valor) for valor in llista_data]
    for valor in llista_data:
        if valor != -inf:
            index = str(valor.index())
            clau_dicc_components = DE + '_' + index
            cridaHypersim = diccionari_components[clau_dicc_components]
            # TODO: utilitzar aquesta linia quan ens conectem a Hypersim
            """HyWorksApi.setComponentParameter(cridaHypersim[0], cridaHypersim[1], valor)"""
    print(f"Dades actualitzades en el {DE}")

def handle_client(client_socket, client_address, port):
    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break  # Sortir del bucle si no hi ha més dades
            if data.startswith(b'ping'):
                pass
            else:
                decoded_data = data.decode('utf-8')
                print(f"Dades rebudes de {client_address}: {decoded_data} a {nom_dispositiu_edge(port)}")
                if data_dict[nom_dispositiu_edge(port)] != decoded_data:
                    comunicate_to_hypersim(decoded_data, port)
            #Response es un exemple
            #response = '163000000,1.025'
            #client_socket.send(response.encode())
    except Exception as e:
        print(f"S'ha produït un error amb el client {client_address}: {e}")
    finally:
        # Tanca la connexió amb aquest client quan surtis del bucle
        client_socket.close()
        print(f"Connexió tancada amb {client_address}")


def receive_data(port):
    host = 'localhost'  # Pots canviar-ho al teu IP si és remot
    while True:
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind((host, port))
            server_socket.listen()
            print(f"Servidor escoltant a {host}:{port}\n")
            while True:
                client_socket, client_address = server_socket.accept()
                print(f"Connexió acceptada des de {client_address}, {nom_dispositiu_edge(port)}")
                handle_client(client_socket, client_address, port)
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

    threads['DE1'] = Thread(target=receive_data, args=(21014,))
    threads['DE2'] = Thread(target=receive_data, args=(21024,))
    threads['DE3'] = Thread(target=receive_data, args=(21034,))
    threads['DE16'] = Thread(target=receive_data, args=(25014,))
    threads['DE17'] = Thread(target=receive_data, args=(25024,))
    threads['DE18'] = Thread(target=receive_data, args=(25034,))

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