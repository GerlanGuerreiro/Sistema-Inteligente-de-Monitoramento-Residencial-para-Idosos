"""
Módulo responsável pela criação das tabelas do sistema.

Executado na inicialização da aplicação.
"""

from banco_dados import obter_conexao

def criar_tabela_eventos():
    """
    Cria tabela de eventos caso não exista.
    """

    conexao = obter_conexao()

    if conexao:
        cursor = conexao.cursor()

        comando_sql = """
        CREATE TABLE IF NOT EXISTS eventos_monitoramento (
            id SERIAL PRIMARY KEY,
            tipo_evento VARCHAR(100),
            objeto_detectado VARCHAR(100),
            horario_evento TIMESTAMP,
            camera VARCHAR(100),
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """

        cursor.execute(comando_sql)
        conexao.commit()

        cursor.close()
        conexao.close()

        print("Tabela eventos_monitoramento verificada/criada.")
