import zmq
import random
import time
import signal
import argparse

from configuracion import IP_PROXY, PUB_PORT_PROXY

# TODO: Hacer que llegue por argumento el archivo de configuracion, leer de este y generar los valores aleatorios

def main():
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

    subscribe_to_topic(args.s, args.t)


def subscribe_to_topic(topic, tiempo):
    signal.signal(signal.SIGINT, signal.SIG_DFL)

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
