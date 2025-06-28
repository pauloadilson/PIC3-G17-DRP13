# --- Estágio 1: Builder ---
# Este estágio instala as dependências em um ambiente temporário e completo.
FROM python:3.11-slim AS builder

# Define variáveis de ambiente para otimizar o Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instala as dependências do sistema operacional necessárias para compilar pacotes Python como o psycopg2
RUN apt-get update \
    && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho para o ambiente virtual
WORKDIR /opt/venv

# Cria um ambiente virtual para isolar as dependências
RUN python -m venv .
ENV PATH="/opt/venv/bin:$PATH"

# Copia e instala as dependências do Python. Esta camada é cacheada para acelerar builds futuros.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Use uma imagem base oficial e leve do Python
FROM python:3.11-slim AS runtime

RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Defina variáveis de ambiente para otimizar o Python em contêineres
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"

# Cria um usuário e grupo não-root para executar a aplicação (prática de segurança)
RUN addgroup --system app && adduser --system --group app

# Define o diretório de trabalho da aplicação
WORKDIR /cpprev

# Copia o ambiente virtual com as dependências já instaladas do estágio 'builder'
COPY --from=builder /opt/venv /opt/venv

# Copia todo o código da aplicação para o diretório de trabalho no contêiner
COPY . /cpprev

# Cria o diretório de estáticos para que o volume possa herdar as permissões corretas
RUN mkdir -p /cpprev/staticfiles

# Define a propriedade dos arquivos para o usuário não-root
RUN chown -R app:app /cpprev

# Muda para o usuário não-root
USER app

# Expõe a porta que o Gunicorn vai usar para a aplicação
EXPOSE 8090

# Comando para iniciar a aplicação (para desenvolvimento local)
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8090"]

# Comando para iniciar a aplicação (para produção)
CMD ["gunicorn", "--bind", "0.0.0.0:8090", "cpprev.wsgi:application"]
