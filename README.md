# Dashboard Voorbij

<p align="center">
  <img src="plaatje/dashboard.png" alt="Dashboard Voorbij" width="420"/>
</p>

<p align="center">
  Persoonlijk homelab-dashboard voor Slackbots, postcode/adres-zoekfuncties, boeken, strips, muziek en service-status.
</p>

---

## Over dit project

**Dashboard Voorbij** is een persoonlijk webdashboard waarin meerdere kleine diensten samenkomen in één overzichtelijke interface.  
Het project is ontstaan uit losse Docker-containers en Slack-integraties en is stap voor stap uitgebreid met zoekfuncties, media-koppelingen, statusblokken en dagelijkse fun-features.

Het dashboard is vooral bedoeld als centrale startpagina voor eigen services in het homelab.

---

## Wat is er toegevoegd?

### Slackbot & dagelijkse features

- Slack-integratie voor eigen slash-commands.
- Dagelijkse of willekeurige quote-functionaliteit.
- Bommel-quotes als speelse dashboard-widget.
- Modulaire opzet zodat nieuwe Slack-routes later makkelijk toegevoegd kunnen worden.

### Postcode zoeken

Zoeken op Nederlandse postcodegegevens via een backend-service.

Ondersteunde zoekvormen:

- Postcode.
- Postcode + huisnummer.
- Teruggeven van adresinformatie zoals straat en plaats.
- Backend-koppeling met PostgreSQL.

### Adres zoeken

Naast zoeken op postcode is er ook adreszoeken toegevoegd.

Ondersteunde zoekvormen:

- Straatnaam + plaatsnaam.
- Fuzzy search voor kleine typefouten.
- Snellere zoekresultaten via een vooraf opgebouwde Fuse.js-index.
- Aparte adresbot-container/service.

### PostgreSQL backend

Het project gebruikt PostgreSQL als databron voor postcode- en adresinformatie.

Toegevoegd:

- PostgreSQL-container voor de postcodegegevens.
- Koppeling vanuit Node.js/Express naar PostgreSQL.
- Gebruik van de tabel met postcode/adresdata.
- Mogelijkheid om vanuit Slack of dashboard-routes queries uit te voeren.

### Fuse.js fuzzy search

Voor straat- en plaatsnamen is Fuse.js toegevoegd, zodat zoeken minder exact hoeft te zijn.

Voordelen:

- Werkt beter bij kleine spelfouten.
- Handig voor straatnamen die lang of lastig te typen zijn.
- Sneller zoeken doordat de index vooraf geladen kan worden.
- Geschikt voor gebruik achter een Slack slash-command.

### Boeken en strips

Het dashboard bevat koppelingen naar media-services.

Toegevoegd:

- Calibre-Web integratie voor boeken.
- Kavita integratie voor strips/comics.
- Visuele blokken voor media.
- Links naar de juiste webinterfaces.
- Ruimte voor covers, metadata en willekeurige aanbevelingen.

### Muziek / Navidrome

Navidrome is toegevoegd als persoonlijke muziekservice.

Belangrijke punten:

- Muziek wordt aangeboden via Docker volumes.
- Host-mappen onder `/mnt` moeten expliciet in de container worden gemount.
- Meerdere muziekbronnen kunnen onder `/music` als submap zichtbaar worden gemaakt.
- Voorbeeld:
  - `/mnt/music` naar `/music/usb1`
  - `/mnt/navidrome-music/usb2` naar `/music/usb2`

### Service-status

Het dashboard bevat statusinformatie voor verschillende services.

Toegevoegd:

- Statusblokken voor eigen containers/services.
- Online/offline-indicatie.
- Visuele stijl met moderne dashboardkaarten.
- Handig om snel te zien of services bereikbaar zijn.

### Docker Compose

De services zijn opgezet rondom Docker en Docker Compose.

Toegevoegd of gebruikt:

- Losse containers voor de verschillende onderdelen.
- Centrale compose-bestanden per service of project.
- Bind mounts voor data en media.
- Mogelijkheid om services snel opnieuw te starten of uit te breiden.

---

## Globale architectuur

```text
Browser / Dashboard
        |
        v
Node.js / Express routes
        |
        +--> PostgreSQL postcode/adres database
        |
        +--> Fuse.js adresindex
        |
        +--> Slack slash-commands
        |
        +--> Calibre-Web
        |
        +--> Kavita
        |
        +--> Navidrome
        |
        +--> Statuschecks voor services
```

---

## Technologieën

- **Node.js**
- **Express**
- **PostgreSQL**
- **Fuse.js**
- **Docker**
- **Docker Compose**
- **Slack API**
- **Calibre-Web**
- **Kavita**
- **Navidrome**
- **ngrok** of reverse proxy voor externe testtoegang

---

## Mogelijke containers/services

Afhankelijk van de lokale setup kunnen deze services aanwezig zijn:

```text
dashboard
slack-postcodebot
slack-adresbot
pg-container
calibre-web
kavita
navidrome
ngrok
```

De exacte containernamen kunnen per omgeving verschillen.

---

## Voorbeeld: Navidrome volumes

Voor meerdere muziekbronnen kan Navidrome zo worden ingericht:

```yaml
services:
  navidrome:
    image: deluan/navidrome:latest
    container_name: navidrome
    ports:
      - "4533:4533"
    restart: unless-stopped
    environment:
      ND_MUSICFOLDER: /music
      ND_DATAFOLDER: /data
      ND_LOGLEVEL: info
      ND_SCANSCHEDULE: 1h
      ND_SESSIONTIMEOUT: 24h
    volumes:
      - /mnt/music:/music/usb1:ro
      - /mnt/navidrome-music/usb2:/music/usb2:ro
      - /opt/navidrome:/data
```

Controleer daarna wat de container werkelijk ziet:

```bash
docker inspect navidrome --format '{{range .Mounts}}{{println .Source "->" .Destination}}{{end}}'
docker exec -it navidrome sh -c 'find /music -maxdepth 2 -type d | sort | head -100'
```

---

## Installatie / starten

Clone de repository:

```bash
git clone https://github.com/stefanv2/dashboard-voorbij.git
cd dashboard-voorbij
```

Installeer dependencies als het dashboard een Node.js-app bevat:

```bash
npm install
```

Start lokaal:

```bash
npm start
```

Of via Docker Compose:

```bash
docker compose up -d
```

Bekijk logs:

```bash
docker compose logs -f
```

Stop de services:

```bash
docker compose down
```

---

## Configuratie

Maak bij voorkeur een `.env` bestand voor lokale instellingen.

Voorbeeld:

```env
PORT=3000

POSTGRES_HOST=192.168.2.11
POSTGRES_PORT=4321
POSTGRES_DB=postcode
POSTGRES_USER=postman
POSTGRES_PASSWORD=changeme

SLACK_SIGNING_SECRET=changeme
SLACK_BOT_TOKEN=changeme
```

Plaats echte wachtwoorden en tokens nooit in GitHub.

---

## Handige controles

Controleer draaiende containers:

```bash
docker ps
```

Controleer logs van een container:

```bash
docker logs -f <containernaam>
```

Controleer of een poort luistert:

```bash
ss -tulpen | grep LISTEN
```

Controleer of een endpoint reageert:

```bash
curl -i http://localhost:3000/
```

---

## Projectstructuur

Een mogelijke structuur:

```text
dashboard-voorbij/
├── README.md
├── docker-compose.yml
├── package.json
├── index.js
├── routes/
│   ├── slack.js
│   ├── postcode.js
│   └── adres.js
├── public/
│   ├── index.html
│   ├── style.css
│   └── plaatje/
└── data/
```

De exacte structuur kan afwijken afhankelijk van welke services in deze repository staan en welke extern via Docker draaien.

---

## Roadmap / ideeën

Mogelijke uitbreidingen:

- Dashboardkaart voor Navidrome met album/trackinformatie.
- Betere healthchecks per container.
- Automatische statuspagina.
- Google Maps-link bij adresresultaten.
- Beheerpagina voor Slackbot-commands.
- Meer dagelijkse widgets, zoals quotes, weer of homelab-status.
- Eén centrale Docker Compose-stack voor alle dashboarddiensten.

---

## Belangrijke notities

- Docker ziet alleen mappen die expliciet als volume zijn gemount.
- Symlinks naar andere `/mnt` locaties werken in containers niet altijd zoals verwacht.
- Bij `autofs` kan een mount pas actief worden nadat de host-map is aangeraakt.
- Controleer daarom bij ontbrekende bestanden altijd zowel de host-map als de container-map.

Voorbeeld:

```bash
ls /mnt/music >/dev/null
docker exec -it navidrome ls -lah /music
```

---

## Licentie

Privé/persoonlijk project. Voeg een officiële licentie toe als deze repository publiek herbruikbaar moet worden.

---

## Auteur

Gemaakt en onderhouden door **Stefan Voorbij**.
