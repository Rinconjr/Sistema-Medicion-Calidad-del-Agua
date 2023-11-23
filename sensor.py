# Ejecucion: python sensor.py -s Topico -t 5

import zmq
import random
import time
import signal
import argparse
import datetime

from configuracion import IP_PROXY, PUB_PORT_PROXY

class sensor:
    #Constructor
    def __init__(self, valor_minimo, valor_maximo):
        self.probabilidades = {}
        self.valor_minimo = valor_minimo
        self.valor_maximo = valor_maximo

    def generar_valor_aleatorio(self):
        eleccion = random.choices(list(self.probabilidades.keys()), weights=list(self.probabilidades.values()))[0]
        if eleccion == "correcto":
            return random.uniform(self.valor_minimo,self.valor_maximo)
        elif eleccion == "fuera_de_rango":
            if random.choice([True,False]):
                return random.uniform(0,self.valor_minimo-1) # Genera un valor menor al minimo
            else:
                return random.uniform(self.valor_maximo+1,100) # Genera un valor mayor al maximo
        else:
            return -random.uniform(self.valor_minimo+1,self.valor_maximo)

    def enviar_topico(self,topic, tiempo):
        context = zmq.Context() # Crea un contexto de comunicación
        socket = context.socket(zmq.PUB)
        socket.connect(f"tcp://{IP_PROXY}:{PUB_PORT_PROXY}") # Asocia el puerto de enlace en la dirección local

        time.sleep(2)  # Espera 2 segundos para dar tiempo al monitor a suscribirse

        print("Sensor activado...")
        
        while True:
            valor = round(float(self.generar_valor_aleatorio()),2)
            fecha_hora_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") #Calcula la fecha y hora actual
            mensaje = f"{topic} {valor} {fecha_hora_actual}"
            socket.send_string(mensaje)
            print(f"Enviando: {mensaje}")
            time.sleep(tiempo)

    def leer_config(self):
        try:
            with open("configuracion.txt", "r") as archivo_config:

                for linea in archivo_config:
                    palabras = linea.strip().split()

                    #Leer probabilidades
                    if len(palabras) == 2:
                        if palabras[0] == "Valores_Correctos":
                            self.probabilidades['correcto'] = float(palabras[1])
                        elif palabras[0] == "Valores_Fuera_De_Rango":
                            self.probabilidades['fuera_de_rango'] = float(palabras[1])
                        elif palabras[0] == "Errores":
                            self.probabilidades['error'] = float(palabras[1])
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

    if args.s == "Temperatura":
        valor_minimo, valor_maximo = 68 , 89
    elif args.s == "PH":
        valor_minimo, valor_maximo = 6.0, 8.0
    else:
        valor_minimo, valor_maximo = 2, 11

    sensor_de_medicion = sensor(valor_minimo,valor_maximo)

    sensor_de_medicion.leer_config()
    sensor_de_medicion.enviar_topico(args.s, args.t)



if __name__ == "__main__":
    main()
