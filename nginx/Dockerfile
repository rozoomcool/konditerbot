FROM nginx:latest

COPY nginx.conf /etc/nginx/nginx.conf

WORKDIR /var/www/html

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]