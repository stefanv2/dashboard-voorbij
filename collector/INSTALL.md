# Installatie van de visitor collector

## 1. Bestanden installeren

Voorbeeldinstallatie onder `/opt`:

    sudo mkdir -p /opt/dashboard-voorbij/collector

    sudo cp visitor_collector.py requirements.txt \
      /opt/dashboard-voorbij/collector/

## 2. Python-afhankelijkheden installeren

    sudo python3 -m pip install \
      -r /opt/dashboard-voorbij/collector/requirements.txt

Een Python virtual environment kan ook worden gebruikt.

## 3. Configuratie installeren

    sudo mkdir -p /etc/dashboard-voorbij

    sudo cp visitors.ini.example \
      /etc/dashboard-voorbij/visitors.ini

    sudo chmod 640 /etc/dashboard-voorbij/visitors.ini

Bewerk daarna de configuratie:

    sudo editor /etc/dashboard-voorbij/visitors.ini

Pas minimaal de volgende instellingen aan:

- `log_glob`
- `public_output`
- `private_output`
- `geoip_db`
- `timezone`
- `own_ips`

## 4. Linux-gebruiker aanmaken

De voorbeeldservice gebruikt de systeemgebruiker `dashboard`.

    sudo useradd \
      --system \
      --home-dir /var/lib/dashboard-voorbij \
      --create-home \
      --shell /usr/sbin/nologin \
      dashboard

Maak de uitvoermappen:

    sudo mkdir -p \
      /var/lib/dashboard-voorbij/public \
      /var/lib/dashboard-voorbij/private

    sudo chown -R dashboard:dashboard \
      /var/lib/dashboard-voorbij

De gebruiker moet leesrechten hebben op de accesslogs van Nginx Proxy
Manager. Gebruik bij voorkeur groepsrechten of een read-only mount.

## 5. GeoLite2 installeren

Download de GeoLite2 Country-database zelf bij MaxMind.

Plaats het bestand bijvoorbeeld als:

    /var/lib/dashboard-voorbij/GeoLite2-Country.mmdb

Geef de collector leesrechten:

    sudo chown dashboard:dashboard \
      /var/lib/dashboard-voorbij/GeoLite2-Country.mmdb

    sudo chmod 640 \
      /var/lib/dashboard-voorbij/GeoLite2-Country.mmdb

## 6. Collector handmatig testen

    sudo -u dashboard \
      /usr/bin/python3 \
      /opt/dashboard-voorbij/collector/visitor_collector.py \
      --config /etc/dashboard-voorbij/visitors.ini

Controleer daarna of de publieke JSON geldig is:

    python3 -m json.tool \
      /var/lib/dashboard-voorbij/public/visitors.json \
      >/dev/null

## 7. Systemd installeren

Controleer eerst de gebruiker en paden in:

    systemd/visitor-dashboard.service

Installeer daarna service en timer:

    sudo cp systemd/visitor-dashboard.service \
      /etc/systemd/system/

    sudo cp systemd/visitor-dashboard.timer \
      /etc/systemd/system/

    sudo systemctl daemon-reload

    sudo systemctl enable --now visitor-dashboard.timer

## 8. Status controleren

    systemctl status visitor-dashboard.timer

    systemctl status visitor-dashboard.service

    journalctl -u visitor-dashboard.service -n 50

De service is van het type `oneshot`. Het is daarom normaal dat de
service na een geslaagde uitvoering als `inactive (dead)` wordt getoond.

## 9. De-installatie

    sudo systemctl disable --now visitor-dashboard.timer

    sudo rm -f \
      /etc/systemd/system/visitor-dashboard.timer \
      /etc/systemd/system/visitor-dashboard.service

    sudo systemctl daemon-reload

Verwijder configuratie en verzamelde data alleen wanneer deze niet meer
nodig zijn.
