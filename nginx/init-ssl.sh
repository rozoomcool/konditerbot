service nginx start

apt-get update && apt-get install python3 python3-venv python3-pip -y
python3 -m venv /venv
/venv/bin/pip install certbot certbot-nginx
#/venv/bin/certbot certonly --standalone --agree-tos --email rosul.um@gmail.com -d ldent.online

#nginx -s reload