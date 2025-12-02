FROM nginx:alpine

# Maak directory schoon
RUN rm -rf /usr/share/nginx/html/*

# Kopieer ALLE bestanden van je dashboard
COPY . /usr/share/nginx/html/

# Nginx serveert automatisch vanaf /usr/share/nginx/html

