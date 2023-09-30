# Ejecucion: python monitor.py -s Topico

import zmq
import argparse

from configuracion import IP_PROXY, SUB_PORT_PROXY

# TODO 2: Revisar porque el primer valor enviado NO llega al monitor.

class monitor:
    def __init__(self,topic):
        self.topic = topic

    def suscribirse_a_topico(self):
        context = zmq.Context() # Crea un contexto de comunicación
        socket = context.socket(zmq.SUB)
        socket.setsockopt_string(zmq.SUBSCRIBE, self.topic)
        socket.connect(f"tcp://{IP_PROXY}:{SUB_PORT_PROXY}")

        while True:
            topic, message = socket.recv_string().split(' ', 1)
            print(f"Recibido en {topic}: Valor: {message}")

def main():

    parser = argparse.ArgumentParser(description="Suscrito a un tópico específico")
    parser.add_argument("-s", choices=["Temperatura", "PH", "Oxigeno"], required=True, help="Tópico al que suscribirse")
    args = parser.parse_args()

    monitor_sistema = monitor(args.s)
    monitor_sistema.suscribirse_a_topico()

if __name__ == "__main__":
    main()
