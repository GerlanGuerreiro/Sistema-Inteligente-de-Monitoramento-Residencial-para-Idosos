"""
SIMULADOR DE EVENTOS DO FRIGATE

Este script publica eventos falsos no MQTT para simular
detecções feitas pelo Frigate.

Útil para testes quando não há câmera conectada.
"""

# ==========================================
# IMPORTAÇÕES
# ==========================================

import json
import time
import random
import paho.mqtt.client as mqtt

# ==========================================
# CONFIGURAÇÃO DO BROKER MQTT
# ==========================================

# Nome do serviço no docker-compose
# Docker cria um DNS interno usando o nome do serviço
BROKER = "broker_mqtt"

# Porta padrão MQTT
PORTA = 1883

TOPICO = "frigate/events"


# ==========================================
# CONEXÃO COM MQTT
# ==========================================

cliente = mqtt.Client()

print("Conectando ao broker MQTT...")

# tenta conexão
cliente.connect(BROKER, PORTA, 60)

print("Conectado com sucesso ao broker MQTT.")

# ==========================================
# FUNÇÃO PARA GERAR EVENTO DE DETECÇÃO
# ==========================================

def gerar_evento_pessoa():

    agora = int(time.time())

    evento = {

        "type": "end",

        "after": {

            # objeto detectado pelo Frigate
            "label": "person",

            # nome da câmera
            "camera": "camera_idoso",

            # tempo de início
            "start_time": agora - 10,

            # tempo de fim
            "end_time": agora,

            # bounding box simulada
            "box": [
                random.randint(100, 200),
                random.randint(50, 150),
                random.randint(300, 500),
                random.randint(200, 350)
            ]
        }
    }

    return evento


# ==========================================
# LOOP DE SIMULAÇÃO
# ==========================================

while True:

    evento = gerar_evento_pessoa()

    mensagem = json.dumps(evento)

    cliente.publish(TOPICO, mensagem)

    print("Evento publicado:", mensagem)

    # espera 10 segundos antes de novo evento
    time.sleep(10)
