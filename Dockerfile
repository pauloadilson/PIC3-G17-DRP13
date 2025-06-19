# Use uma imagem base oficial e leve do Python
FROM python:3.11-slim

# Defina variáveis de ambiente para otimizar o Python em contêineres
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Crie e defina o diretório de trabalho dentro do contêiner
WORKDIR /cpprev

# Copie o arquivo de dependências
COPY requirements.txt .

# Instale as dependências do sistema necessárias para compilar psycopg2 e outras extensões C
# libpq-dev: para psycopg2
# gcc: compilador C, frequentemente necessário para outras dependências
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Instale as dependências (incluindo psycopg2-binary)
RUN pip install --no-cache-dir -r requirements.txt

# Copie todo o código do projeto para o diretório de trabalho no contêiner
COPY . .

# Exponha a porta que a aplicação usará
EXPOSE 8090

# Comando para iniciar a aplicação (para desenvolvimento local)
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8090"]

# Comando para iniciar a aplicação (para produção)
CMD ["gunicorn", "--bind", "0.0.0.0:8090", "cpprev.wsgi:application"]
