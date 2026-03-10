"""
Módulo responsável por lógica de monitoramento do idoso.

Funções implementadas:

- Registrar última vez que pessoa foi vista
- Detectar ausência prolongada
- Gerar alertas
"""

from datetime import datetime, timedelta

# tempo máximo permitido sem detectar pessoa
TEMPO_MAXIMO_SEM_PESSOA = timedelta(minutes=2)

# variável global simples (poderia ir para Redis ou banco)
ultimo_horario_pessoa = None


def registrar_presenca(horario_evento):
    """
    Atualiza último horário em que pessoa foi detectada.
    """

    global ultimo_horario_pessoa
    ultimo_horario_pessoa = horario_evento

    print("Presença registrada:", horario_evento)


def verificar_inatividade():
    """
    Verifica se pessoa não foi detectada por muito tempo.
    """

    global ultimo_horario_pessoa

    if ultimo_horario_pessoa is None:
        return

    agora = datetime.now()

    tempo_sem_pessoa = agora - ultimo_horario_pessoa

    if tempo_sem_pessoa > TEMPO_MAXIMO_SEM_PESSOA:

        gerar_alerta(
            tipo="inatividade",
            mensagem="Nenhuma pessoa detectada há muito tempo"
        )


def gerar_alerta(tipo, mensagem):
    """
    Gera alerta simples no console.
    Futuramente pode enviar:
    - WhatsApp
    - Telegram
    - App mobile
    """

    print("🚨 ALERTA:", tipo)
    print("Mensagem:", mensagem)
