"""
Módulo responsável por enviar notificações
e imagens para o Telegram.
"""

import os
import requests
from dotenv import load_dotenv

# ==========================================
# CARREGAR VARIÁVEIS DO .env
# ==========================================

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


# ==========================================
# ENVIAR MENSAGEM SIMPLES
# ==========================================

def enviar_alerta_telegram(mensagem):
    """
    Envia mensagem simples para Telegram.
    """

    if not TOKEN or not CHAT_ID:
        print("Telegram não configurado.")
        return

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": mensagem
    }

    requests.post(url, json=payload)

    print("Mensagem enviada ao Telegram.")


# ==========================================
# ENVIAR FOTO PARA TELEGRAM
# ==========================================

def enviar_foto_telegram(caminho_imagem, legenda):

    """
    Envia snapshot da câmera para Telegram.
    """

    if not os.path.exists(caminho_imagem):
        print("Imagem não encontrada:", caminho_imagem)
        return

    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"

    files = {
        "photo": open(caminho_imagem, "rb")
    }

    data = {
        "chat_id": CHAT_ID,
        "caption": legenda
    }

    try:

        requests.post(url, files=files, data=data)

        print("Foto enviada ao Telegram.")

    except Exception as erro:

        print("Erro ao enviar foto:", erro)
