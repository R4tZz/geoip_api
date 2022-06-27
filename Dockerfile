FROM python:latest

EXPOSE 8000

ARG SECRET_KEY
ARG API_IPSTACK_KEY
ARG MYSQL_HOST
ARG MYSQL_PORT
ARG MYSQL_DATABASE_NAME
ARG MYSQL_USER
ARG MYSQL_PASSWORD
ARG ACCESS_TOKEN_EXPIRE_MINUTES
ARG ALGORITHM


RUN [ -z "$SECRET_KEY" ] && echo "SECRET_KEY is required" && exit 1 || true
RUN [ -z "$API_IPSTACK_KEY" ] && echo "API_IPSTACK_KEY is required" && exit 1 || true
RUN [ -z "$MYSQL_HOST" ] && echo "MYSQL_HOST is required" && exit 1 || true
RUN [ -z "$MYSQL_PORT" ] && echo "MYSQL_PORT is required" && exit 1 || true
RUN [ -z "$MYSQL_DATABASE_NAME" ] && echo "MYSQL_DATABASE_NAME is required" && exit 1 || true
RUN [ -z "$MYSQL_USER" ] && echo "MYSQL_USER is required" && exit 1 || true
RUN [ -z "$MYSQL_PASSWORD" ] && echo "MYSQL_PASSWORD is required" && exit 1 || true
RUN [ -z "$ACCESS_TOKEN_EXPIRE_MINUTES" ] && echo "ACCESS_TOKEN_EXPIRE_MINUTES is required" && exit 1 || true
RUN [ -z "$ALGORITHM" ] && echo "ALGORITHM is required" && exit 1 || true


# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

#ENV
ENV YOUR_ENV=geoip_api
ENV SECRET_KEY=${SECRET_KEY}
ENV API_IPSTACK_KEY=${API_IPSTACK_KEY}
ENV MYSQL_HOST=${MYSQL_HOST}
ENV MYSQL_PORT=${MYSQL_PORT}
ENV MYSQL_DATABASE_NAME=${MYSQL_DATABASE_NAME}
ENV MYSQL_USER=${MYSQL_USER}
ENV MYSQL_PASSWORD=${MYSQL_PASSWORD}
ENV ACCESS_TOKEN_EXPIRE_MINUTES=${ACCESS_TOKEN_EXPIRE_MINUTES}
ENV ALGORITHM=${ALGORITHM}

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]