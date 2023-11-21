# Ejecucion: python monitor.py -s Topico

import zmq
import argparse
import threading

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime

from configuracion import IP_PROXY, SUB_PORT_PROXY, IP_CALIDAD, PORT_CALIDAD

# TODO 2: Revisar porque el primer valor enviado NO llega al monitor.

class monitor:
    def __init__(self,topic):
        self.topic = topic
        self.valor_minimo = 0
        self.valor_maximo = 0

    def suscribirse_a_topico(self):
        context = zmq.Context() # Crea un contexto de comunicación
        socket = context.socket(zmq.SUB)
        socket.setsockopt_string(zmq.SUBSCRIBE, self.topic)
        socket.connect(f"tcp://{IP_PROXY}:{SUB_PORT_PROXY}")

        if self.topic == "Temperatura":
            self.valor_minimo, self.valor_maximo = 68 , 89
        elif self.topic == "PH":
            self.valor_minimo, self.valor_maximo = 6.0, 8.0
        else:
            self.valor_minimo, self.valor_maximo = 2, 11

        print(f"Monitor activado para el tópico {self.topic}...")

        while True:
            topic, valor, fecha_hora = socket.recv_string().split(' ', 2)
            fecha_hora = datetime.strptime(fecha_hora, "%Y-%m-%d %H:%M:%S")
            print(f"Recibido en: {topic}, Valor: {valor} Fecha y hora: {fecha_hora}")
            valor = float(valor)
            self.revisar_valor(valor, fecha_hora)


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
        if valor < self.valor_minimo or valor > self.valor_maximo:
            mensaje = f"{self.topic} fuera de rango {valor}"

            def enviar_a_calidad(mensaje):
                context = zmq.Context()
                socket = context.socket(zmq.PUSH)
                socket.connect(f"tcp://{IP_CALIDAD}:{PORT_CALIDAD}")  # Ajusta la dirección y el puerto según tus necesidades
                socket.send_string(mensaje)
                socket.close()

            # Crear y ejecutar el hilo para el envío del mensaje
            thread = threading.Thread(target=enviar_a_calidad, args=(mensaje,))
            thread.start()

    def enviar_dato_BDD(self,valor, fecha_hora):
        uri = "mongodb+srv://nicorinconb:8uDjmict3XYbu00H@sistemacalidadagua.hyxzpxx.mongodb.net/?retryWrites=true&w=majority&tlsAllowInvalidCertificates=true"
        #Crear cliente para conectarse a la base de datos
        client = MongoClient(uri, server_api=ServerApi('1'))
        db = client['calidadAgua']
        collection = db['mediciones']

        collection.insert_one(self.convertir_a_json(self.topic, valor, fecha_hora))

    # Convertir a json para enviar a la base de datos
    def convertir_a_json(self, topic, valor, fecha_hora):
        return {
            "topico": topic,
            "valor": valor,
            "fecha_hora": fecha_hora.strftime("%Y-%m-%d %H:%M:%S")
            }

def main():

    parser = argparse.ArgumentParser(description="Suscrito a un tópico específico")
    parser.add_argument("-s", choices=["Temperatura", "PH", "Oxigeno"], required=True, help="Tópico al que suscribirse")
    args = parser.parse_args()

    monitor_sistema = monitor(args.s)
    monitor_sistema.suscribirse_a_topico()

if __name__ == "__main__":
    main()
