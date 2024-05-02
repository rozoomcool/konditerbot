FROM nginx:latest

COPY nginx.conf /etc/nginx/nginx.conf

WORKDIR /var/www/html

EXPOSE 3000
EXPOSE 443

#COPY init-ssl.sh .
#
#RUN chmod +x init-ssl.sh
#
#RUN /bin/sh -c "./init-ssl.sh"

CMD ["nginx", "-g", "daemon off;"]