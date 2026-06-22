FROM nginx:alpine

# Maak standaard nginx html-directory schoon
RUN rm -rf /usr/share/nginx/html/*

# Gebruik onze eigen nginx-config met /api proxy
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Kopieer dashboard-bestanden
COPY . /usr/share/nginx/html/

EXPOSE 80
