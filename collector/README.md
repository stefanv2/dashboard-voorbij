# Visitor & Security Collector

De collector analyseert accesslogs van Nginx Proxy Manager en publiceert
JSON-data voor het Home Operations Center-dashboard.

## Functies

- Bezoekers en sessies per website
- Unieke externe bezoekers
- Bot- en scannerdetectie
- Detectie van `.env`, WordPress, PHPUnit, Laravel en path-traversal probes
- GeoIP-landherkenning
- Publieke en private JSON-uitvoer
- Automatische herkenning van hosts uit de logs
- Uitvoering via een systemd-timer

## Vereisten

- Linux
- Python 3.10 of nieuwer
- Nginx Proxy Manager-accesslogs
- Python-pakket `geoip2`
- Optioneel: MaxMind GeoLite2 Country

Installeer de Python-afhankelijkheden:

    python3 -m pip install -r requirements.txt

## Configuratie

Kopieer de voorbeeldconfiguratie:

    sudo mkdir -p /etc/dashboard-voorbij
    sudo cp visitors.ini.example /etc/dashboard-voorbij/visitors.ini

Pas daarna minimaal deze instellingen aan:

    log_glob = /pad/naar/nginx-proxy-manager/logs/proxy-host-*_access.log*
    public_output = /pad/naar/dashboard/minecraft-status/visitors.json
    private_output = /veilig/prive/pad/visitors-private.json
    geoip_db = /pad/naar/GeoLite2-Country.mmdb

`own_ips` kan één of meerdere publieke IP-adressen bevatten:

    own_ips = 203.0.113.10, 203.0.113.11

Laat `own_ips` leeg wanneer eigen verkeer niet apart hoeft te worden
herkend.

## Handmatig uitvoeren

    python3 visitor_collector.py \
      --config /etc/dashboard-voorbij/visitors.ini

Voor een specifieke datum:

    python3 visitor_collector.py \
      --config /etc/dashboard-voorbij/visitors.ini \
      --date 2026-07-16

## Uitvoer

De publieke JSON is bedoeld voor het dashboard.

De private JSON kan bronbestanden, eigen IP-adressen, sessiegegevens en
niet-herkende logregels bevatten. Plaats deze daarom nooit in een publieke
webroot.

## Privacy

Commit nooit:

- `visitors.ini`
- runtime-JSON
- GeoIP `.mmdb`-bestanden
- accesslogs
- eigen IP-adressen
- back-ups van de collector

## GeoLite2

De GeoLite2-database is niet opgenomen in deze repository. Download zelf
de GeoLite2 Country-database bij MaxMind en configureer het lokale pad in
`visitors.ini`.

## Securityscore

De v6.1-score beschrijft vooral de hoeveelheid verdachte activiteit.
Een hoge score is niet automatisch bewijs van een geslaagde aanval.

In v6.2 wordt onderscheid gemaakt tussen:

- Internet Noise
- Werkelijk Security Risk
- Bevestigde kwetsbaarheden
- Onschuldige HTML- en SPA-fallbackpagina's
