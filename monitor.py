import zmq
import argparse
import threading
import time
import socket
import os

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
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
                topic, valor, fecha_hora = socket.recv_string().split(' ', 2)
                fecha_hora = datetime.strptime(fecha_hora, "%Y-%m-%d %H:%M:%S")
                print(f"Recibido en: {topic}, Valor: {valor}, Fecha y hora: {fecha_hora}")
                valor = float(valor)
                self.revisar_valor(valor, fecha_hora)
            except zmq.ContextTerminated:
                print("Contexto de zmq terminado. Saliendo...")
                break

    def revisar_valor(self, valor, fecha_hora):
        if valor >= self.valor_minimo and valor <= self.valor_maximo:
            print("Correcto")
            self.enviar_dato_BDD(valor, fecha_hora)
        elif valor < 0:
            print("Incorrecto")
        else:
            print("fuera_de_rango")
            self.enviar_alarma(valor)
            self.enviar_dato_BDD(valor, fecha_hora)

    def enviar_alarma(self, valor):
        if valor < self.valor_minimo:
            mensaje = f"{self.topic} debajo del mínimo {valor}."
        else:
            mensaje = f"{self.topic} arriba del máximo {valor}."

        def enviar_a_calidad(mensaje):
            context = zmq.Context()
            socket = context.socket(zmq.PUSH)
            socket.connect(f"tcp://{IP_CALIDAD}:{PORT_CALIDAD}")
            socket.send_string(mensaje)
            socket.close()

        thread = threading.Thread(target=enviar_a_calidad, args=(mensaje,), daemon=True)
        thread.start()

    def enviar_dato_BDD(self, valor, fecha_hora):
        uri = "mongodb+srv://nicorinconb:8uDjmict3XYbu00H@sistemacalidadagua.hyxzpxx.mongodb.net/?retryWrites=true&w=majority&tlsAllowInvalidCertificates=true"
        client = MongoClient(uri, server_api=ServerApi('1'))
        db = client['calidadAgua']
        collection = db['mediciones']

        collection.insert_one(self.convertir_a_json(self.topic, valor,fecha_hora))

    def convertir_a_json(self, topic, valor, fecha_hora):
        return {
            "topico": topic,
            "valor": valor,
            "fecha_hora": fecha_hora.strftime("%Y-%m-%d %H:%M:%S")
        }

    def enviar_mensaje(self,ip, pid):
        context = zmq.Context()
        socket_pub = context.socket(zmq.PUB)
        socket_pub.connect("tcp://127.0.0.1:5555")
        while True:
            try:
                context = zmq.Context()
                # Socket para enviar datos
                
                mensaje = '{"ip": "'+ str(ip)+'", "pid": '+ str(pid) +', "tipo": "'+ self.topic +'", "mensaje": "OK"}'
                socket_pub.send_string(str(mensaje))
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
