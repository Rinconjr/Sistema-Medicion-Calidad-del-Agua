import zmq
import argparse

def subscribe_to_topic(topic):
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.setsockopt_string(zmq.SUBSCRIBE, topic)
    socket.connect("tcp://127.0.0.1:5555")

    while True:
        topic, message = socket.recv_string().split(' ', 1)
        print(f"Recibido en {topic}: {message}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Suscrito a un tópico específico")
    parser.add_argument("topic", choices=["temperatura", "PH", "Oxigeno"], help="Tópico al que suscribirse")
    args = parser.parse_args()

    subscribe_to_topic(args.topic)