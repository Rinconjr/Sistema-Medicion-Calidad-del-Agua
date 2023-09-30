# Ejecución: python proxy.py

import zmq

from configuracion import SUB_PORT_PROXY, PUB_PORT_PROXY

class proxy:
    def __init__(self):
        self.context = zmq.Context()
        self.frontend = None
        self.backend = None
    
    def crear_socket_XPUB(self):
        self.frontend = self.context.socket(zmq.XPUB)
        self.frontend.bind(f"tcp://*:{SUB_PORT_PROXY}")
        print(f"Creado socket tipo XPUB con puerto: {SUB_PORT_PROXY}")

    def crear_socket_XSUB(self):
        self.backend = self.context.socket(zmq.XSUB)
        self.backend.bind(f"tcp://*:{PUB_PORT_PROXY}")
        print(f"Creado socket tipo XSUB con puerto: {PUB_PORT_PROXY}")
    
    def crear_proxy(self):
        zmq.proxy(self.frontend, self.backend)

        self.frontend.close()
        self.backend.close()
        self.context.term()

def main():
    proxy_sistema = proxy()
    proxy_sistema.crear_socket_XPUB()
    proxy_sistema.crear_socket_XSUB()
    proxy_sistema.crear_proxy()
    

if __name__ == "__main__":
    main()