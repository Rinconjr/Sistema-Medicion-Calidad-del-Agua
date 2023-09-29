import zmq
import signal

from configuracion import SUB_PORT_PROXY, PUB_PORT_PROXY

def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    context = zmq.Context() # Crea un contexto de comunicación

    # Socket tipo XPUB
    frontend = context.socket(zmq.XPUB)
    frontend.bind(f"tcp://*:{SUB_PORT_PROXY}")

    print(f"Creado socket tipo XPUB con puerto: {SUB_PORT_PROXY}")

    # Socket tipo XSUB
    backend = context.socket(zmq.XSUB)
    backend.bind(f"tcp://*:{PUB_PORT_PROXY}")

    print(f"Creado socket tipo XSUB con puerto: {PUB_PORT_PROXY}")

    # Crear proxy
    zmq.proxy(frontend, backend)

    frontend.close()
    backend.close()
    context.term()

if __name__ == "__main__":
    main()