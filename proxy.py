import zmq
import signal

from configuracion import SUB_PORT_PROXY, PUB_PORT_PROXY

def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    context = zmq.Context()

    # Socket tipo XPUB
    frontend = context.socket(zmq.XPUB)
    frontend.bind(f"tcp://*:{SUB_PORT_PROXY}")

    # Socket tipo XSUB
    backend = context.socket(zmq.XSUB)
    backend.bind(f"tcp://*:{PUB_PORT_PROXY}")

    # Crear proxy
    zmq.proxy(frontend, backend)

    # We never get here…
    frontend.close()
    backend.close()
    context.term()

if __name__ == "__main__":
    main()