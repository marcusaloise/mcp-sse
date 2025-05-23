FROM python:3.10-slim

# Instale dependências do sistema
RUN apt-get update && apt-get install -y gcc libffi-dev && rm -rf /var/lib/apt/lists/*

# Crie diretório do app
WORKDIR /app

# Instale dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie o código
COPY . .

# Exponha a porta (opcional, mas bom para documentação)
EXPOSE 8000 

# Comando para rodar o servidor
CMD ["python", "mcp_sse.py"]
