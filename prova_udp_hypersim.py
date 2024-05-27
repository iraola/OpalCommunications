import socket
import signal

def signal_handler(signal, frame):
    print('\nInterrupció de teclat detectada. Finalitzant el programa...')
    sock.close()
    exit(0)

# Configurar la funció de gestió de senyals per a la interrupció de teclat
signal.signal(signal.SIGINT, signal_handler)

# Crear un socket UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Enllaçar el socket a l'adreça IP i port locals
port = 21002
# sock.bind(('192.168.0.16', port))
sock.bind(('127.0.0.1', port))

print(f'El programa està escoltant al port {port}...')

# Establir un temps d'espera de 5 segons per als missatges entrants
sock.settimeout(3)

# Escoltar els missatges entrants
while True:
    try:
        print("Esperant dades...")
        data, addr = sock.recvfrom(1024)
        print('Dades rebudes:', data)
    except socket.timeout:
        print("No s'han rebut dades en els últims 5 segons")
    except KeyboardInterrupt:
        print('\nInterrupció de teclat detectada. Finalitzant el programa...')
        sock.close()
        exit(0)