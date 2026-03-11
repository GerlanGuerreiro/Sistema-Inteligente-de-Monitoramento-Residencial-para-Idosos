"""
Arquivo principal da API.

Responsável por:

- Inicializar servidor FastAPI
- Iniciar consumidor MQTT
"""

from fastapi import FastAPI
from consumidor_mqtt import iniciar_consumidor, iniciar_monitoramento
from modelos import criar_tabela_eventos, criar_tabela_alertas

app = FastAPI(
    title="API de Monitoramento Inteligente",
    description="Sistema acadêmico de monitoramento residencial com IA",
    version="1.0.0"
)

# ==========================================
# EVENTO DE INICIALIZAÇÃO DA APLICAÇÃO
# ==========================================

@app.on_event("startup")
def ao_iniciar_aplicacao():

    print("Criando/verificando tabelas...")
    criar_tabela_eventos()
    criar_tabela_alertas()

    print("Iniciando consumidor MQTT...")
    iniciar_consumidor()

    print("Iniciando monitoramento do idoso...")
    iniciar_monitoramento()


@app.get("/")
def rota_inicial():
    """
    Endpoint de verificação.
    """

    return {"mensagem": "API em execução com consumidor MQTT ativo."}
