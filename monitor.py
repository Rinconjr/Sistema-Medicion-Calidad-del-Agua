import zmq
import argparse
import threading
import time
import socket
import os

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from configuracion import IP_PROXY, SUB_PORT_PROXY, IP_CALIDAD, PORT_CALIDAD, IP_HEALTHCHECK, PORT_HEALTHCHECK

class monitor:
    def __init__(self, topic):
        self.topic = topic
        self.valor_minimo = 0
        self.valor_maximo = 0
        self.is_running = True

    def suscribirse_a_topico(self):
        context = zmq.Context()
        socket = context.socket(zmq.SUB)
        socket.setsockopt_string(zmq.SUBSCRIBE, self.topic)
        socket.connect(f"tcp://{IP_PROXY}:{SUB_PORT_PROXY}")

        if self.topic == "Temperatura":
            self.valor_minimo, self.valor_maximo = 68, 89
        elif self.topic == "PH":
            self.valor_minimo, self.valor_maximo = 6.0, 8.0
        else:
            self.valor_minimo, self.valor_maximo = 2, 11

        print(f"Monitor activado para el tópico {self.topic}...")

        while self.is_running:
            try:
                topic, message = socket.recv_string().split(' ', 1)
                print(f"Recibido en {topic}: Valor: {message}")
                self.revisar_valor(float(message))
            except zmq.ContextTerminated:
                print("Contexto de zmq terminado. Saliendo...")
                break

    def revisar_valor(self, valor):
        if valor >= self.valor_minimo and valor <= self.valor_maximo:
            print("Correcto")
            self.enviar_dato_BDD(valor)
        elif valor < 0:
            print("Incorrecto")
        else:
            print("fuera_de_rango")
            self.enviar_alarma(valor)
            self.enviar_dato_BDD(valor)

    def enviar_alarma(self, valor):
        if valor < self.valor_minimo or valor > self.valor_maximo:
            mensaje = f"{self.topic} fuera de rango {valor}"

            def enviar_a_calidad(mensaje):
                context = zmq.Context()
                socket = context.socket(zmq.PUSH)
                socket.connect(f"tcp://{IP_CALIDAD}:{PORT_CALIDAD}")
                socket.send_string(mensaje)
                socket.close()

            thread = threading.Thread(target=enviar_a_calidad, args=(mensaje,), daemon=True)
            thread.start()

    def enviar_dato_BDD(self, valor):
        uri = "mongodb+srv://nicorinconb:8uDjmict3XYbu00H@sistemacalidadagua.hyxzpxx.mongodb.net/?retryWrites=true&w=majority&tlsAllowInvalidCertificates=true"
        client = MongoClient(uri, server_api=ServerApi('1'))
        db = client['calidadAgua']
        collection = db['mediciones']

        collection.insert_one(self.convertir_a_json(self.topic, valor))

    def convertir_a_json(self, topic, valor):
        return {
            "topico": topic,
            "valor": valor
        }

    def enviar_mensaje(self,ip, pid):
        while True:
            try:
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect((IP_HEALTHCHECK, PORT_HEALTHCHECK))
                mensaje = '{"ip": "'+ str(ip)+'", "pid": '+ str(pid) +', "tipo": "'+ self.topic +'", "mensaje": "OK"}'
                client_socket.sendall(mensaje.encode())
                client_socket.close()
                time.sleep(1)
            except (ConnectionRefusedError, OSError):
                print("Error de conexión. Saliendo...")
                break

def main():
    parser = argparse.ArgumentParser(description="Suscrito a un tópico específico")
    parser.add_argument("-s", choices=["Temperatura", "PH", "Oxigeno"], required=True, help="Tópico al que suscribirse")
    args = parser.parse_args()

    monitor_sistema = monitor(args.s)
    monitor_thread = threading.Thread(target=monitor_sistema.suscribirse_a_topico, daemon=True)
    monitor_thread.start()

    host_name = socket.gethostname()
    mi_ip = socket.gethostbyname(host_name)
    mi_pid = os.getpid()

    healthcheck_thread = threading.Thread(target=monitor_sistema.enviar_mensaje, args=(mi_ip, mi_pid), daemon=True)
    healthcheck_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Programa terminado por el usuario.")
        monitor_sistema.is_running = False
        exit(1)

if __name__ == "__main__":
    main()
