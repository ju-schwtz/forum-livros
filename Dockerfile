# Usar uma imagem base com Python
FROM python:3.9-slim

# Instalar dependências do sistema para compilar mysqlclient
RUN apt-get update && \
    apt-get install -y \
    pkg-config \
    libmariadb-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Definir o diretório de trabalho
WORKDIR /forum

# Copiar o requirements.txt e instalar as dependências
COPY requirements.txt /forum/
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo o código da aplicação para o diretório de trabalho dentro do container
COPY . /forum/

# Expor a porta em que o Flask estará rodando
EXPOSE 5000

# Rodar a aplicação Flask
CMD ["flask", "run", "--host=0.0.0.0"]
