import zmq
import random
import time
import signal

from configuracion import IP_PROXY, PUB_PORT_PROXY

def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.connect(f"tcp://{IP_PROXY}:{PUB_PORT_PROXY}") #Asocia el puerto de enlace en la direccion local

    topicos = ["Temperatura", "PH", "Oxigeno"]

    while True:
        topic = random.choice(topicos)
        mensaje = f"Random {random.randint(0, 10)} "
        print(f"Publicando en {topic}")
        socket.send_string(f"{topic} {mensaje}")
        time.sleep(1)

if __name__ == "__main__":
    main()