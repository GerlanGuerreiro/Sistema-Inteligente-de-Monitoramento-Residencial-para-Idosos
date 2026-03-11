"""
Módulo responsável por conectar ao broker MQTT
e consumir eventos publicados pelo Frigate.
"""

# ==========================================
# IMPORTAÇÕES
# ==========================================

import os
import json
import paho.mqtt.client as mqtt
import threading
import time

from dotenv import load_dotenv
from datetime import datetime, timedelta

from banco_dados import obter_conexao
from monitoramento_idoso import verificar_inatividade, verificar_queda
from analise_comportamento import registrar_evento
from notificador import enviar_alerta_telegram, enviar_foto_telegram


# ==========================================
# CARREGAR VARIÁVEIS DE AMBIENTE
# ==========================================

load_dotenv()

endereco_broker = os.getenv("ENDERECO_BROKER_MQTT", "broker_mqtt")
porta_broker = int(os.getenv("PORTA_BROKER_MQTT", 1883))

usuario_mqtt = os.getenv("USUARIO_MQTT")
senha_mqtt = os.getenv("SENHA_MQTT")

topico_eventos = "frigate/events"


# ==========================================
# CONFIGURAÇÕES DO SISTEMA
# ==========================================

INTERVALO_MINIMO_EVENTO = timedelta(seconds=30)
TEMPO_IMOBILIDADE = timedelta(minutes=2)
DISTANCIA_MINIMA_MOVIMENTO = 50


# ==========================================
# BUFFERS DE MEMÓRIA
# ==========================================

ultimo_evento_camera = {}
historico_posicoes = {}


# ==========================================
# CONTROLE DE ANTI-SPAM
# ==========================================

def deve_registrar_evento(camera):

    agora = datetime.now()
    ultimo = ultimo_evento_camera.get(camera)

    if ultimo is None:
        ultimo_evento_camera[camera] = agora
        return True

    if agora - ultimo > INTERVALO_MINIMO_EVENTO:
        ultimo_evento_camera[camera] = agora
        return True

    return False


# ==========================================
# DETECÇÃO DE PESSOA PARADA
# ==========================================

def verificar_pessoa_parada(camera, bbox):

    agora = datetime.now()

    centro_x = (bbox[0] + bbox[2]) / 2
    centro_y = (bbox[1] + bbox[3]) / 2

    posicao_atual = (centro_x, centro_y)

    dados = historico_posicoes.get(camera)

    if dados is None:

        historico_posicoes[camera] = {
            "posicao": posicao_atual,
            "tempo": agora
        }

        return None

    posicao_antiga = dados["posicao"]
    tempo_antigo = dados["tempo"]

    distancia = (
        (posicao_atual[0] - posicao_antiga[0]) ** 2 +
        (posicao_atual[1] - posicao_antiga[1]) ** 2
    ) ** 0.5

    if distancia > DISTANCIA_MINIMA_MOVIMENTO:

        historico_posicoes[camera] = {
            "posicao": posicao_atual,
            "tempo": agora
        }

        return None

    if agora - tempo_antigo > TEMPO_IMOBILIDADE:

        return {
            "tipo_alerta": "pessoa_imovel",
            "camera": camera,
            "tempo_parado": str(agora - tempo_antigo)
        }

    return None


# ==========================================
# CONEXÃO MQTT
# ==========================================

def ao_conectar(cliente, dados_usuario, flags, codigo_retorno):

    if codigo_retorno == 0:

        print("Conectado ao broker MQTT")

        cliente.subscribe(topico_eventos)

        print("Inscrito no tópico:", topico_eventos)

    else:

        print("Falha ao conectar no broker MQTT")


# ==========================================
# PROCESSAMENTO DAS MENSAGENS
# ==========================================

def ao_receber_mensagem(cliente, dados_usuario, mensagem):

    try:

        carga_util = json.loads(mensagem.payload.decode())

        tipo_evento = carga_util.get("type")
        dados_evento = carga_util.get("after")

        if not dados_evento:
            return

        objeto = dados_evento.get("label")
        camera = dados_evento.get("camera")
        inicio = dados_evento.get("start_time")
        fim = dados_evento.get("end_time")
        bbox = dados_evento.get("box")

        # evita spam de eventos
        if not deve_registrar_evento(camera):
            return


        # ==========================================
        # EVENTO FINALIZADO
        # ==========================================

        if tipo_evento == "end" and objeto == "person":

            print("Evento finalizado detectado")

            registrar_evento_banco(
                objeto,
                camera,
                inicio,
                fim
            )


        # ==========================================
        # DETECÇÃO DE PESSOA
        # ==========================================

        if objeto == "person":

            print("Pessoa detectada:", camera)

            registrar_evento(camera)


            # ==========================================
            # DETECÇÃO DE QUEDA
            # ==========================================

            if bbox:

                alerta_queda = verificar_queda(camera, bbox)

                if alerta_queda:

                    print("🚨 POSSÍVEL QUEDA DETECTADA")

                    snapshot = None

                    if inicio:
                        snapshot = f"/media/frigate/clips/{camera}-{int(inicio)}.jpg"

                    registrar_alerta(
                        alerta_queda["tipo_alerta"],
                        alerta_queda["camera"],
                        str(alerta_queda),
                        snapshot
                    )


            # ==========================================
            # DETECÇÃO DE IMOBILIDADE
            # ==========================================

            if bbox:

                alerta_imobilidade = verificar_pessoa_parada(camera, bbox)

                if alerta_imobilidade:

                    print("⚠ Pessoa parada detectada")

                    snapshot = None

                    if inicio:
                        snapshot = f"/media/frigate/clips/{camera}-{int(inicio)}.jpg"

                    registrar_alerta(
                        alerta_imobilidade["tipo_alerta"],
                        alerta_imobilidade["camera"],
                        str(alerta_imobilidade),
                        snapshot
                    )

    except Exception as erro:

        print("Erro ao processar mensagem MQTT:", erro)


# ==========================================
# INICIALIZA CONSUMIDOR MQTT
# ==========================================

def iniciar_consumidor():

    cliente = mqtt.Client()

    if usuario_mqtt and senha_mqtt:
        cliente.username_pw_set(usuario_mqtt, senha_mqtt)

    cliente.on_connect = ao_conectar
    cliente.on_message = ao_receber_mensagem

    cliente.connect(endereco_broker, porta_broker, 60)

    cliente.loop_start()


# ==========================================
# REGISTRO DE EVENTOS NO BANCO
# ==========================================

def registrar_evento_banco(objeto, camera, inicio, fim):

    conexao = obter_conexao()

    if not conexao:
        return

    cursor = conexao.cursor()

    duracao = int(fim - inicio)

    cursor.execute(
        """
        INSERT INTO eventos_monitoramento
        (
            tipo_evento,
            objeto_detectado,
            camera,
            inicio_evento,
            fim_evento,
            duracao_segundos
        )
        VALUES (%s,%s,%s,%s,%s,%s)
        """,
        (
            "deteccao",
            objeto,
            camera,
            datetime.fromtimestamp(inicio),
            datetime.fromtimestamp(fim),
            duracao
        )
    )

    conexao.commit()

    cursor.close()
    conexao.close()

    print("Evento salvo no banco")


# ==========================================
# REGISTRO DE ALERTAS
# ==========================================

def registrar_alerta(tipo, camera, descricao, snapshot=None):

    conexao = obter_conexao()

    if conexao:

        cursor = conexao.cursor()

        cursor.execute(
            """
            INSERT INTO alertas (tipo_alerta, camera, descricao)
            VALUES (%s,%s,%s)
            """,
            (tipo, camera, descricao)
        )

        conexao.commit()

        cursor.close()
        conexao.close()

        print("Alerta salvo no banco")


    mensagem = f"""
🚨 ALERTA DETECTADO

Tipo: {tipo}
Camera: {camera}

{descricao}
"""

    enviar_alerta_telegram(mensagem)

    if snapshot:
        enviar_foto_telegram(snapshot, mensagem)


# ==========================================
# LOOP DE MONITORAMENTO
# ==========================================

def loop_monitoramento():

    while True:

        verificar_inatividade()

        time.sleep(10)


# ==========================================
# INICIAR THREAD
# ==========================================

def iniciar_monitoramento():

    thread = threading.Thread(target=loop_monitoramento)

    thread.daemon = True

    thread.start()
