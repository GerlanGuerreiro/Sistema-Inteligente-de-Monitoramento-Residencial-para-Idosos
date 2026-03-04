"""
Módulo responsável pela conexão com o banco de dados PostgreSQL.

Implementa:

- Conexão segura via variáveis de ambiente
- Função para obter conexão ativa
"""

import os
import psycopg2
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

def obter_conexao():
    """
    Cria e retorna conexão com o banco PostgreSQL.
    """

    try:
        conexao = psycopg2.connect(
            host="banco_dados",  # Nome do serviço no docker-compose
            database=os.getenv("NOME_BANCO"),
            user=os.getenv("USUARIO_BANCO"),
            password=os.getenv("SENHA_BANCO")
        )

        return conexao

    except Exception as erro:
        print("Erro ao conectar ao banco:", erro)
        return None
