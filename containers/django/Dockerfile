FROM alpine:latest

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update && apk upgrade && apk add --no-cache  build-base \
    python3-dev \
    libffi-dev \
    openssl-dev \
    py3-pip \
    tzdata;

WORKDIR /app

COPY simplified_prj ./
RUN mkdir -p /var/media/avatars/ && mv media/avatars/default.jpg /var/media/avatars/
COPY requirements.txt ./
COPY entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh
RUN cp /usr/share/zoneinfo/Europe/Paris /etc/localtime

RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

CMD ["entrypoint.sh"]