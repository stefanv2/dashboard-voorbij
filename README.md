# Voorbij Slackbot & Dashboard

---

<p align="center">
<img src="plaatje/dashboard.png" alt="BTOP" width="400" height="400"/>  
</p>

---
# Dashboard Voorbij

Een modern en persoonlijk webdashboard dat verschillende microservices, databronnen en tools samenbrengt in één stijlvolle interface. Het project draait volledig in Docker en biedt zowel praktische functionaliteit als leuke dagelijkse features.

---

## ✨ Functionaliteiten

### 🦝 Bommel-Quotes
Een speels onderdeel dat bij elke pagina-verversing een nieuwe, willekeurige Bommel-quote presenteert. Licht, humoristisch en helemaal in stijl.

### 🏠 Postcode & Adres Zoeker
Zoek razendsnel naar adressen via:
- Postcode + huisnummer  
- Straatnaam + plaats  
- Fuzzy search voor spellingsvarianten  

Technologie: **PostgreSQL** + **Fuse.js**.

### 📚 Boeken & Strips (Calibre / Kavita)
Het dashboard toont je collectie in een nette, moderne lay-out:
- Mooie cover-weergave  
- Beschrijvingen en metadata  
- Links naar Calibre-Web  
- Willekeurige boek/strip voor inspiratie  

### 🟢 Online Status Indicatoren
Een helder statusblok dat toont welke services online zijn:  
Boekenpagina, comicpagina, Slack-services en meer.  
Met zachte neon glow voor snelle herkenning.

---

## 🧱 Architectuur

Het project gebruikt een modulair ontwerp zodat onderdelen eenvoudig uitbreidbaar zijn.

### 🔧 Technologieën
- **Node.js** backend  
- **Express** voor API-routes  
- **PostgreSQL** voor opslag en queries  
- **Fuse.js** voor fuzzy matching  
- **Calibre-Web** en **Kavita** voor media  
- **Docker Compose** voor orchestratie  
- **ngrok** of **Nginx Proxy Manager** voor externe toegang  
- **Slack API** voor slash-commands en bots  

### 📦 Microservices / Containers
- `slack-postcodebot`
- `slack-adresbot`
- `calibre-web`
- `kavita`
- `pg-container` (PostgreSQL)
- `dashboard` (front-end)

---

## 📸 Illustratie

Hieronder een moderne flat-stijl illustratie van het dashboardconcept:

*(voeg hier de gegenereerde afbeelding toe in GitHub)*  
```markdown
![Dashboard Voorbij Illustratie](./illustratie.png)

