# 🌍 Voorbij Slackbot & Dashboard

Een persoonlijk project waarin **Slack-integratie**, **PostgreSQL** en een **visueel dashboard** samenkomen.  
De bot beantwoordt Slack-commando’s (zoals `/adres` en `/postcode`), terwijl het dashboard real-time informatie en kaarten toont.  
Gebouwd in **Node.js**, **Express**, en gedraaid in Docker-containers.

---

## ⚙️ Functies

- 🔎 **Fuzzy search** (Fuse.js) op straat- en plaatsnamen  
- 🗺️ Integratie met **Google Maps / OpenStreetMap**  
- 💬 **Slack-slash-commands** (`/adres`, `/postcode`, `/grafiek`, …)  
- 💾 Backend met **PostgreSQL** (container `pg-container`)  
- 🌐 Frontend-dashboard met HTML + CSS  
- 🐳 Klaar voor gebruik via **Docker Compose**

---

## 🧩 Projectstructuur

mijn_postgres_slackbot/
├── Dockerfile
├── docker-compose.yml
├── index.html # Dashboard UI
├── style.css # Stijlen voor het dashboard
├── routes/ # Slack-routes
│ ├── slack.js
│ └── slack-adres.js
├── fuse-data.json # Vooraf geladen zoekindex
├── .env.example # Voorbeeld van omgevingsvariabelen
├── package.json
└── .gitignore

yaml
Code kopiëren

---

## 🚀 Gebruik

### 1️⃣ Bouw en start met Docker
```bash
docker build -t slack-postcodebot .
docker run -d --name slack-postcodebot -p 3002:3002 slack-postcodebot
Of gebruik docker-compose:

bash
Code kopiëren
docker-compose up -d
2️⃣ Voorbeeld .env
Maak een .env bestand op basis van .env.example:

ini
Code kopiëren
SLACK_BOT_TOKEN=xoxb-xxxxxxxxxxxxx
SLACK_SIGNING_SECRET=xxxxxx
DB_HOST=pg-container
DB_PORT=5432
DB_USER=postman
DB_PASS=*****
DB_NAME=postcode
PUBLIC_URL_SLACK=https://voorbij.duckdns.org
3️⃣ Test lokaal
Start de server handmatig:

bash
Code kopiëren
npm install
npm start
Bezoek:

arduino
Code kopiëren
http://localhost:3002
🧠 Technologieën
Component	Technologie
Slack integratie	Slack API + Express
Database	PostgreSQL
Search	Fuse.js
Containerisatie	Docker
Frontend	HTML + CSS + JS

📦 Deployment
Push image naar lokale registry (optioneel):

bash
Code kopiëren
docker push 192.168.2.11:5000/slack-postcodebot:latest
Gebruik Nginx Proxy Manager of reverse proxy voor HTTPS.

Gebruik ngrok of DuckDNS voor publieke toegang.

🧰 Handige commando’s
Doel	Commando
Logs bekijken	docker logs -f slack-postcodebot
Container herstarten	docker restart slack-postcodebot
Lokale rebuild	docker compose build --no-cache

🧑‍💻 Auteur
Stefan V.
Oracle DBA • PostgreSQL & Linux admin
GitHub: stefanv2

"Soms is één query genoeg om je hele wereld te veranderen." 💡
