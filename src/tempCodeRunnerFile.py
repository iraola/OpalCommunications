def enviar_dades_thread(objecte):
    while True:
        dades_a_enviar = b''
        objecte.check_and_reconnect()
        data_list = actualitzar_dades(objecte.nom)   #Funcio per llegir noves dades d'Hypersim
        for f_value in data_list:
            dades_a_enviar += struct.pack('f', float(f_value))
        objecte.enviar_dades_tcp(struct.pack('!I', len(dades_a_enviar)))
        objecte.enviar_dades_tcp(dades_a_enviar)
        objecte.enviar_dades_tcp(b'\n')
        time.sleep(5)