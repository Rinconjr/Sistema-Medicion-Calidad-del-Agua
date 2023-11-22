import socket
import threading
import time
import json
import datetime
import zmq

import os
from configuracion import IP_HEALTHCHECK, PORT_HEALTHCHECK

monitores = []
mutex = threading.Lock()

class healthcheck:
    def __init__(self):
        self.is_running = True

    def healthcheck_server(self):
        context = zmq.Context()

        # Socket para recibir datos
        receiver_socket = context.socket(zmq.PULL)
        receiver_socket.bind(f"tcp://{IP_HEALTHCHECK}:{PORT_HEALTHCHECK}")
        
        #server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #server_socket.bind((IP_HEALTHCHECK, PORT_HEALTHCHECK))
        #server_socket.listen(5)
        print(f"Healthcheck server en el puerto {PORT_HEALTHCHECK}")

        while True:
            mensaje = receiver_socket.recv_string()

            datos_json = json.loads(mensaje)

            found = False
            with mutex:
                for monitor in monitores:
                    if monitor["pid"] == datos_json["pid"]:
                        monitor["datetime"] = datetime.datetime.now()
                        found = True
                        break

                # Si el monitor es nuevo
                if not found:
                    datos_json["datetime"] = datetime.datetime.now()
                    monitores.append(datos_json)
                    print("Se ha añadido un nuevo monitor. " + str(datos_json["tipo"]))
                
                print("Se ha reportado " + str(datos_json["tipo"]))

    def verificar_procesos(self):
        timeout = 5
        while True:
            hora_actual = datetime.datetime.now()
            with mutex:
                for monitor in monitores:
                    # Si al cabo de 5 segundos el monitor no se reporta, se da por muerto
                    if (hora_actual - monitor["datetime"]).total_seconds() > timeout:
                        print("El monitor de tipo " + str(monitor["tipo"]) + " ha muerto")
                        tipoMonitor = str(monitor["tipo"])
                        monitores.remove(monitor)
                        os.system('start cmd /k python monitor.py -s ' + tipoMonitor) # Tengan cuidado si van a editar esta parte del codigo porque pueden abrir terminales recursivamente                        

if __name__ == "__main__":
    health = healthcheck()
    # Iniciar el servidor healthcheck en un hilo daemon
    healthcheck_thread = threading.Thread(target=health.healthcheck_server, args=(), daemon=True)
    healthcheck_thread.start()

    # Verificar procesos en un hilo daemon
    verificar_thread = threading.Thread(target=health.verificar_procesos, args=(), daemon=True)
    verificar_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Programa terminado por el usuario.")
        health.is_running = False
        exit(1)
