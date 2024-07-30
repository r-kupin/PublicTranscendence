FROM alpine:latest

RUN	apk update && apk upgrade && apk add --no-cache nginx openssl

RUN mkdir -p /etc/nginx/ssl \
&& openssl req -x509 -nodes -out /etc/nginx/ssl/trans.crt \
-keyout /etc/nginx/ssl/trans.key -subj "/CN=trans"

COPY entrypoint.sh ./
RUN chmod +x entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]