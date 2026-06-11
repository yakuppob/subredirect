FROM nginx:alpine

# Nginx ayar dosyamızı içeri kopyalıyoruz
COPY nginx.conf /etc/nginx/nginx.conf

# Cloud Run varsayılan portu
EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
