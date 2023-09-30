# Ejecucion: python monitor.py -s Topico

import zmq
import argparse
import signal

from configuracion import IP_PROXY, SUB_PORT_PROXY

# TODO 2: Revisar porque el primer valor enviado NO llega al monitor.

def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    parser = argparse.ArgumentParser(description="Suscrito a un tópico específico")
    parser.add_argument("-s", choices=["Temperatura", "PH", "Oxigeno"], required=True, help="Tópico al que suscribirse")
    args = parser.parse_args()

    subscribe_to_topic(args.s)

def subscribe_to_topic(topic):
    context = zmq.Context() # Crea un contexto de comunicación
    socket = context.socket(zmq.SUB)
    socket.setsockopt_string(zmq.SUBSCRIBE, topic)
    socket.connect(f"tcp://{IP_PROXY}:{SUB_PORT_PROXY}")

    while True:
        topic, message = socket.recv_string().split(' ', 1)
        print(f"Recibido en {topic}: Valor: {message}")

if __name__ == "__main__":
    main()
