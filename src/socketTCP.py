import socket
import time

class socketTCP:
    def __init__(self, port, nom):
        self.nom = nom[0] #SM1, Ld1, Cb1        # Ara mateix nomes es te en compte un node per edge (ex: {"20001":["SM1", "CB1"]} --> {"20001":["SM1"]})
        self.portClient = int(port) - 1
        self.portServer = int(port)
        self.socketDE = None

    # Funcio que es fa servir per obrir el socket (en els ports que escollim) i connectar-se al servidor.
    def setup_tcp(self):
        localIP = 'localhost'
        serverIP = 'localhost'
        # S'obre un socket TCP i s'escullen els ports que es volen fer servir en l'enviament.
        self.socketDE = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socketDE.bind((localIP, self.portClient))
        self.socketDE.settimeout(5)
        try:
            # Intentem connectar-nos amb el servidor.
            self.socketDE.connect((serverIP, self.portServer))
            print(f'Connectant a {serverIP} per port {self.portServer} ({self.nom})')
        except OSError as e:
            print(f'Error en la connexió: {e}')
            self.socketDE = None

    # Funcio que fem servir per enviar dades a través del socket creat.
    def enviar_dades_tcp(self, dades):
        # Comprova si hi ha connexió.
        if self.socketDE is None:
            print("El socket no està configurat. Executa setup_tcp abans d'enviar dades.")
        else:
            try:
                self.socketDE.send(dades)
                print(f"Enviant a {dades}...")
                print(f"Enviant a {self.nom}...")
                # Això no se si cal.
                """if resposta == b'done':
                    print('done')
                    time.sleep(1)"""
            except OSError as e:
                print(f"Error en l'enviament de dades {self.nom}: {e}")
                self.socketDE = None

    # Funció que comprova que la connexió segueix activa i gestiona self.socketDE. I
    def check_and_reconnect(self):
        while True:
            try:
                if self.socketDE is not None:
                    # self.socketDE.send(b'ping')
                    pass
                else:
                    self.setup_tcp()
            except OSError as e:
                print(f'Error en la connexió {self.nom}: {e}')
                self.socketDE = None
                # Espera abans de tornar a intentar la connexió
                print(f'Esperant abans de tornar a intentar la connexió a {self.nom}...')
                time.sleep(5)  # Canvia a la quantitat de temps entre reintents
                continue
            break  # Si arriba aquí, la connexió és exitosa i surt del bucle

