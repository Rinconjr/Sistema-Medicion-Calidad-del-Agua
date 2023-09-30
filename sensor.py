# Ejecucion: python sensor.py -s Topico -t 5

import zmq
import random
import time
import signal
import argparse

from configuracion import IP_PROXY, PUB_PORT_PROXY

# TODO 1: Hacer que llegue por argumento el archivo de configuracion, leer de este y generar los valores aleatorios para enviar a los monitores.

def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    parser = argparse.ArgumentParser(description="Suscripción a un tópico específico")
    parser.add_argument("-s", choices=["Temperatura", "PH", "Oxigeno"], help="Tópico al que suscribirse")
    parser.add_argument("-t", type=int, help="Intervalo de tiempo en segundos")
    args = parser.parse_args()

    if not args.s:
        print("Debes especificar un tópico usando la opción -s.")
        return

    if args.t is None or args.t <= 0:
        print("Debes proporcionar un valor válido para el intervalo de tiempo (-t) mayor que 0.")
        return

    send_topic(args.s, args.t)


def send_topic(topic, tiempo):
    context = zmq.Context() # Crea un contexto de comunicación
    socket = context.socket(zmq.PUB)
    socket.connect(f"tcp://{IP_PROXY}:{PUB_PORT_PROXY}") # Asocia el puerto de enlace en la dirección local

    while True:
        mensaje = f"Random {random.randint(0, 10)} "
        print(f"Publicando en {topic}")
        socket.send_string(f"{topic} {mensaje}")
        time.sleep(tiempo)

if __name__ == "__main__":
    main()
