FROM alpine:latest

RUN	apk update && apk upgrade && apk add --no-cache nginx openssl

RUN mkdir -p /etc/nginx/ssl \
&& openssl req -x509 -nodes -out /etc/nginx/ssl/trans.crt \
-keyout /etc/nginx/ssl/trans.key -subj "/CN=trans"

COPY conf/nginx.conf /etc/nginx/http.d
COPY replace.sh ./
RUN chmod +x replace.sh &&  \
    ./replace.sh "ssl_protocols TLSv1.1 TLSv1.2 TLSv1.3;" \
    "ssl_protocols TLSv1.2;" \
    "/etc/nginx/nginx.conf"

CMD ["nginx", "-g", "daemon off;"]

