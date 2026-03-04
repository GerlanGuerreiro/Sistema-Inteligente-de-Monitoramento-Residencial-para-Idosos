# Imagem base oficial do Python
FROM python:3.11-slim

# Define diretório de trabalho
WORKDIR /aplicacao

# Copia arquivos para dentro do container
COPY requisitos.txt .

# Instala dependências
RUN pip install --no-cache-dir -r requisitos.txt

# Copia restante do código
COPY . .

# Comando para iniciar API
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
