# Ejecucion: python sensor.py -s Topico -t 5

import zmq
import random
import time
import signal
import argparse

from configuracion import IP_PROXY, PUB_PORT_PROXY

# TODO 1: Hacer que llegue por argumento el archivo de configuracion, leer de este y generar los valores aleatorios para enviar a los monitores.

probabilidades = {}

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

    valor_minimo, valor_maximo = leer_config(args.s)
    send_topic(args.s, args.t, valor_minimo, valor_maximo)


def send_topic(topic, tiempo, valor_minimo,valor_maximo):
    context = zmq.Context() # Crea un contexto de comunicación
    socket = context.socket(zmq.PUB)
    socket.connect(f"tcp://{IP_PROXY}:{PUB_PORT_PROXY}") # Asocia el puerto de enlace en la dirección local
    
    while True:
        eleccion = random.choices(list(probabilidades.keys()), weights=list(probabilidades.values()))[0]
        if eleccion == "correcto":
            valor = random.randint(valor_minimo,valor_maximo)
            print(f"Correcto {valor}")
        elif eleccion == "fuera_de_rango":
            valor = random.randint(valor_minimo,valor_maximo)+valor_maximo
            print(f"Fuera {valor}")
        else:
            valor = -random.randint(valor_minimo,valor_maximo)
            print(f"Error {valor}")

        mensaje = f"Random {valor} "
        print(f"Publicando en {topic}")
        socket.send_string(f"{topic} {mensaje}")
        time.sleep(tiempo)

def leer_config(topic):
    try:
        with open("configuracion.txt", "r") as archivo_config:

            for linea in archivo_config:
                palabras = linea.strip().split()

                #Leer probabilidades
                if len(palabras) == 2:
                    if palabras[0] == "Valores_Correctos":
                        probabilidades['correcto'] = float(palabras[1])
                    elif palabras[0] == "Valores_Fuera_De_Rango":
                        probabilidades['fuera_de_rango'] = float(palabras[1])
                    elif palabras[0] == "Errores":
                        probabilidades['error'] = float(palabras[1])
                
                #Leer rango
                elif len(palabras) == 3:
                    if palabras[0] == topic:
                        valor_minimo = palabras[1]
                        valor_maximo = palabras[2]

    except Exception as e:
        print(f"Ocurrió un error inesperado: {str(e)}")
        exit(1)
    return int(valor_minimo),int(valor_maximo)

if __name__ == "__main__":
    main()
