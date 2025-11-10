FROM nginx:alpine

# Verwijder standaard website
RUN rm -rf /usr/share/nginx/html/*

# Kopieer jouw dashboard
COPY index.html /usr/share/nginx/html/index.html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

