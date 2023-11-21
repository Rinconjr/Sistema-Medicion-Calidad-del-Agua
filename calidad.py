# En calidad.py

import zmq

from configuracion import IP_CALIDAD, PORT_CALIDAD

def recibir_alarma():
    context = zmq.Context()
    socket = context.socket(zmq.PULL)
    socket.bind(f"tcp://{IP_CALIDAD}:{PORT_CALIDAD}")  # Escuchando en localhost (127.0.0.1) en el puerto 5555

    while True:
        mensaje = socket.recv_string()
        print(f"{mensaje}")

if __name__ == "__main__":
    print("El módulo 'calidad' se está ejecutando directamente.")

    recibir_alarma()