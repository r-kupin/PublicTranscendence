#!/bin/sh

# create current nginx.conf
if [ ! -d "/etc/nginx/http.d" ]; then
  mkdir "/etc/nginx/http.d"
else
  rm /etc/nginx/http.d/*
fi


cat << EOF > /etc/nginx/http.d/nginx.conf
server {
    listen      443 ssl;
    server_name ${HOST};
    root        /var/static/;

	add_header X-Content-Type-Options "nosniff";

    ssl_certificate 	/etc/nginx/ssl/trans.crt;
    ssl_certificate_key 	/etc/nginx/ssl/trans.key;

    location / {
        proxy_pass http://django:8000;
        proxy_set_header Host \$http_host;
        proxy_redirect off;
        proxy_set_header X-Forwarded-For \$remote_addr;
        proxy_set_header X-Forwarded-Proto \$scheme;
        client_max_body_size 20m;
    }

    location /static/ {
        alias /var/static/;
    }

    location /media/ {
        alias /var/media/;
    }

    location /wss/ {
        proxy_pass http://django:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }
}
EOF
# use TLSv1.2 only
sed -i "s/TLSv1.1 TLSv1.2 TLSv1.3/TLSv1.2/" /etc/nginx/nginx.conf

nginx

tail -f /var/log/nginx/access.log /var/log/nginx/error.log