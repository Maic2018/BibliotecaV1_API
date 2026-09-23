FROM python:3.11-slim

WORKDIR /app

# Instala as dependências primeiro para aproveitar o cache de camadas do Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código da API
COPY . .

EXPOSE 5000

# host 0.0.0.0 é necessário para a API ficar acessível fora do container
CMD ["python", "app.py"]
