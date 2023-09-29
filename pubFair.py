import zmq
import random
import time

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://127.0.0.1:5555") #Asocia el puerto de enlace en la direccion local

topicos = ["temperatura", "PH", "Oxigeno"]

while True:
    topic = random.choice(topicos)
    mensaje = f"Random {random.randint(0, 10)} "
    print(f"Publicando en {topic}")
    socket.send_string(f"{topic} {mensaje}")
    time.sleep(1)
