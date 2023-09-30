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
    global valor_minimo, valor_maximo
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


    if args.s == "Temperatura":
        valor_minimo, valor_maximo = 68 , 89
    elif args.s == "PH":
        valor_minimo, valor_maximo = 6.0, 8.0
    else:
        valor_minimo, valor_maximo = 2, 11

    leer_config()
    send_topic(args.s, args.t)

def generateRandomValue():
    eleccion = random.choices(list(probabilidades.keys()), weights=list(probabilidades.values()))[0]
    if eleccion == "correcto":
        print("Se generara un valor correcto")
        return random.randint(valor_minimo,valor_maximo)
    elif eleccion == "fuera_de_rango":
        print("Se generara un valor fuera de rango")
        return random.randint(valor_minimo,valor_maximo)+valor_maximo
    else:
        print("Se generara un valor incorrecto")
        return -random.randint(valor_minimo,valor_maximo)


def send_topic(topic, tiempo):
    context = zmq.Context() # Crea un contexto de comunicación
    socket = context.socket(zmq.PUB)
    socket.connect(f"tcp://{IP_PROXY}:{PUB_PORT_PROXY}") # Asocia el puerto de enlace en la dirección local
    
    while True:
        valor = generateRandomValue()

        mensaje = f"Random {valor} "
        print(f"Publicando en {topic} con valor {mensaje}")
        socket.send_string(f"{topic} {mensaje}")
        time.sleep(tiempo)

def leer_config():

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
                    else:
                        raise ValueError("")

                else:
                    raise ValueError("")

    except ValueError:
        print("Error de argumentos, revise que la informacion en configuracion.txt esta bien escrita")
        exit(1)
    except Exception as e:
        print(f"Ocurrió un error inesperado: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()
