# Ejecucion: python monitor.py -s Topico

import zmq
import argparse

from configuracion import IP_PROXY, SUB_PORT_PROXY

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

        while True:
            topic, message = socket.recv_string().split(' ', 1)
            print(f"Recibido en {topic}: Valor: {message}")
            self.revisar_valor(float(message))

    def revisar_valor(self, valor):
        if valor >= self.valor_minimo and valor <= self.valor_maximo:
            print("Correcto")
            self.enviar_datos_BDD(valor)
        elif valor < 0:
            print("Incorrecto")
        else:
            print("fuera_de_rango")
            self.enviar_alarma(valor)
            self.enviar_datos_BDD(valor)

    def enviar_alarma(self,valor):
        #print("CALIDAD")

    def enviar_datos_BDD(self,valor):
        #print("BDD")

    def enviar_dato_BDD_replica(self,valor):
        #print("Replica")

def main():

    parser = argparse.ArgumentParser(description="Suscrito a un tópico específico")
    parser.add_argument("-s", choices=["Temperatura", "PH", "Oxigeno"], required=True, help="Tópico al que suscribirse")
    args = parser.parse_args()

    monitor_sistema = monitor(args.s)
    monitor_sistema.suscribirse_a_topico()

if __name__ == "__main__":
    main()
