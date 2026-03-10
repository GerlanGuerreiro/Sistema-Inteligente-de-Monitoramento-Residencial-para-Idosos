"""
Módulo responsável por conectar ao broker MQTT
e consumir eventos publicados pelo Frigate.

Este módulo realiza:

- Conexão com o broker
- Inscrição no tópico de eventos
- Processamento das mensagens recebidas
"""

import os
import json
import paho.mqtt.client as mqtt
import threading
import time
from monitoramento_idoso import verificar_inatividade
from dotenv import load_dotenv
from banco_dados import obter_conexao
from datetime import datetime
from monitoramento_idoso import registrar_presenca

# ==========================================
# CARREGAR VARIÁVEIS DO ARQUIVO .env
# ==========================================

load_dotenv()

endereco_broker = os.getenv("ENDERECO_BROKER_MQTT", "broker_mqtt")
porta_broker = int(os.getenv("PORTA_BROKER_MQTT", 1883))
usuario_mqtt = os.getenv("USUARIO_MQTT")
senha_mqtt = os.getenv("SENHA_MQTT")

topico_eventos = "frigate/events"

# ==========================================
# FUNÇÃO EXECUTADA AO CONECTAR AO BROKER
# ==========================================

def ao_conectar(cliente, dados_usuario, flags, codigo_retorno):
    """
    Executada automaticamente quando o cliente
    estabelece conexão com o broker MQTT.
    """

    if codigo_retorno == 0:
        print("Conectado ao broker MQTT com sucesso.")
        cliente.subscribe(topico_eventos)
        print(f"Inscrito no tópico: {topico_eventos}")
    else:
        print("Falha na conexão com o broker MQTT.")

# ==========================================
# FUNÇÃO EXECUTADA AO RECEBER MENSAGEM
# ==========================================

def ao_receber_mensagem(cliente, dados_usuario, mensagem):
    """
    Processa mensagens recebidas do Frigate.
    """

    try:

        carga_util = json.loads(mensagem.payload.decode())

        tipo_evento = carga_util.get("type")
        dados_evento = carga_util.get("after")

        # Ignora mensagens que não são eventos novos
        if tipo_evento != "new" or not dados_evento:
            return

        objeto_detectado = dados_evento.get("label")
        horario_inicio = dados_evento.get("start_time")
        nome_camera = dados_evento.get("camera")

        # Verifica se objeto detectado é pessoa
        if objeto_detectado == "person":

            print("Pessoa detectada. Registrando no banco...")

            registrar_evento_banco(
                tipo_evento="deteccao_pessoa",
                objeto_detectado=objeto_detectado,
                horario_evento=horario_inicio,
                camera=nome_camera
            )

    except Exception as erro:
        print("Erro ao processar mensagem MQTT:", erro)

# ==========================================
# FUNÇÃO PRINCIPAL DE INICIALIZAÇÃO
# ==========================================

def iniciar_consumidor():
    """
    Cria cliente MQTT e inicia escuta de eventos.
    """

    cliente = mqtt.Client()

    if usuario_mqtt and senha_mqtt:
        cliente.username_pw_set(usuario_mqtt, senha_mqtt)

    cliente.on_connect = ao_conectar
    cliente.on_message = ao_receber_mensagem

    cliente.connect(endereco_broker, porta_broker, 60)

    # Loop infinito para escutar mensagens
    cliente.loop_start()


# ==========================================
# INSERE EVENTOS NO BANCO DE DADOS
# ==========================================

def registrar_evento_banco(tipo_evento, objeto_detectado, horario_evento, camera):
    """
    Insere evento detectado na tabela do banco.
    """

    conexao = obter_conexao()

    if conexao:
        cursor = conexao.cursor()

        comando_sql = """
        INSERT INTO eventos_monitoramento
        (tipo_evento, objeto_detectado, horario_evento, camera)
        VALUES (%s, %s, %s, %s);
        """

        cursor.execute(
            comando_sql,
            (
                tipo_evento,
                objeto_detectado,
                datetime.fromtimestamp(horario_evento),
                camera
            )
        )

        conexao.commit()

        cursor.close()
        conexao.close()

        print("Evento registrado no banco com sucesso.")


# ==========================================
# VERIFICADOR PERIÓDICO
# ==========================================
def loop_monitoramento():
    """
    Loop que verifica inatividade periodicamente.
    """

    while True:
        verificar_inatividade()
        time.sleep(30)


def iniciar_monitoramento():
    """
    Inicia thread paralela de monitoramento.
    """

    thread = threading.Thread(target=loop_monitoramento)
    thread.daemon = True
    thread.start()

