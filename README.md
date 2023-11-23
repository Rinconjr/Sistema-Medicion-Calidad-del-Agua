# Sistema Medición Calidad del Agua
Proyecto para la materia Introducción a Sistemas Distribuidos

## Requisitos
Instalar ZeroMQ para Python:

    pip install pyzmq

## Ejecución
Proxy: 

    python proxy.py

Monitor: 

    python monitor.py -s topico

Sensor:

    python sensor.py -s topico -t 5

Calidad:

    python calidad.py

HealthCheck:

    python healthcheck.py
