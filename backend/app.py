import paho.mqtt.client as mqtt
import time

mqtt_client = None

# =================================
# Quando conecta (ou reconecta)
# =================================
def on_connect(client, userdata, flags, rc):

    if rc == 0:
        print("MQTT conectado com sucesso.")

        # IMPORTANTE:
        # precisamos reinscrever após reconexão
        client.subscribe(MQTT_TOPIC)

        print("Inscrito novamente no tópico:", MQTT_TOPIC)

    else:
        print("Falha ao conectar. Código:", rc)

# =================================
# Quando desconecta
# =================================
def on_disconnect(client, userdata, rc):

    print("MQTT desconectado. Código:", rc)

    # rc != 0 significa desconexão inesperada
    if rc != 0:
        print("Tentando reconectar automaticamente...")

        reconnect(client)

# =================================
# Reconexão com tentativa infinita
# =================================
def reconnect(client):

    while True:
        try:
            client.reconnect()
            print("Reconectado ao MQTT.")
            return
        except:
            print("Falha na reconexão. Tentando novamente em 5s...")
            time.sleep(5)

# =================================
# Recebimento de mensagens
# =================================
def on_message(client, userdata, msg):

    mensagem = msg.payload.decode()
    print("Alerta recebido:", mensagem)

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO alertas (mensagem) VALUES (%s)",
            (mensagem,)
        )

        conn.commit()
        cur.close()
        conn.close()

        print("Alerta salvo no banco.")

    except Exception as e:
        print("Erro ao salvar alerta:", e)

# =================================
# Inicialização MQTT
# =================================
def start_mqtt():

    global mqtt_client

    mqtt_client = mqtt.Client()

    mqtt_client.on_connect = on_connect
    mqtt_client.on_disconnect = on_disconnect
    mqtt_client.on_message = on_message

    print("Conectando ao broker MQTT...")

    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)

    mqtt_client.loop_forever()
