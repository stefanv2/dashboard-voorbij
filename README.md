# üåç Voorbij Slackbot & Dashboard

---

<p align="center">
<img src="plaatje/dashboard.png" alt="BTOP" width="400" height="400"/>  
</p>

---

?? Over dit project ó Dashboard Voorbij

Dashboard Voorbij is een persoonlijk, multifunctioneel startportaal dat allerlei handige tools en microservices samenbrengt in ÈÈn overzichtelijke webinterface. Het dashboard draait volledig in Docker en combineert zowel technische features als leuke dagelijkse hulpmiddelen. Alles is ontworpen met een strakke, moderne UI met zachte neon-accenten.

? Wat kun je ermee?
?? Bommel-Quotes

Elke keer dat je de pagina opent krijg je een nieuwe, willekeurige Bommel-quote te zien ó een lichte, speelse touch die het dashboard karakter geeft.

?? Postcode & Adres Zoeker

Zoek op adres, straatnaam of postcode. Dankzij een combinatie van PostgreSQL en slimme fuzzy search krijg je razendsnel relevante resultaten.

?? Boeken & Strips via Calibre/Kavita

Je kunt direct bladeren door je boekencollectie of strips:

Mooie coverweergave

Overzichtelijke kaartjes

ìBekijk in Calibre-Webî-linkjes voor direct openen

Willekeurige boek/strip feature voor inspiratie

?? Online Status Indicators

In ÈÈn oogopslag zie je of de microservices achter je dashboard online zijn:

Boeken pagina

Comics pagina

Je eigen (slack) bots
De lampjes hebben een zachte glow, zodat de status meteen duidelijk is.

?? Onder de motorkap

Het dashboard gebruikt:

Node.js voor APIís en communicatie

Express routes voor Slack, adressen en boeken

PostgreSQL voor snelle zoekopdrachten

Fuse.js voor fuzzy matching van adressen

Docker Compose voor alle containers

Calibre-Web en Kavita voor boeken & stripcollecties

ngrok of Nginx Proxy Manager voor externe toegang

Alles is modulair opgezet zodat onderdelen eenvoudig uitbreidbaar zijn.

?? Doel van het project

Dit dashboard is meer dan een verzameling scripts. Het is een centraal punt waar:

Hobbyprojecten samenkomen

Data uit verschillende bronnen netjes wordt gepresenteerd

Slack-bots en externe services eenvoudig kunnen integreren

Je dagelijks gemak Èn plezier uit haalt

Het doel is vooral: praktisch, mooi en leuk om te gebruiken.

Wil je dat ik dit stukje nog uitbreid met bijvoorbeeld:

? Installatie-instructies
? Architectuurschets
? Screenshots-sectie
? Badges (Docker, Node.js, PostgreSQL)
? Toekomstige plannen / TODO-lijst
? Credits-sectie

Zeg het maar ó ik schrijf het graag voor je verder.

Je zei:
Kun je een readme.md hiervan maken?
ChatGPT zei:

Hier is een complete, kant-en-klare README.md voor jouw Dashboard Voorbij project.
Strak, modern, duidelijk ó en perfect geschikt voor GitHub.

# Dashboard Voorbij

Een modern en persoonlijk webdashboard dat verschillende microservices, databronnen en tools samenbrengt in ÈÈn stijlvolle interface. Het project draait volledig in Docker en biedt zowel praktische functionaliteit als leuke dagelijkse features.

---

## ? Functionaliteiten

### ?? Bommel-Quotes
Een speels onderdeel dat bij elke pagina-verversing een nieuwe, willekeurige Bommel-quote presenteert. Licht, humoristisch en helemaal in stijl.

### ?? Postcode & Adres Zoeker
Zoek razendsnel naar adressen via:
- Postcode + huisnummer  
- Straatnaam + plaats  
- Fuzzy search voor spellingsvarianten  

Technologie: **PostgreSQL** + **Fuse.js**.

### ?? Boeken & Strips (Calibre / Kavita)
Het dashboard toont je collectie in een nette, moderne lay-out:
- Mooie cover-weergave  
- Beschrijvingen en metadata  
- Links naar Calibre-Web  
- Willekeurige boek/strip voor inspiratie  

### ?? Online Status Indicatoren
Een helder statusblok dat toont welke services online zijn:  
Boekenpagina, comicpagina, Slack-services en meer.  
Met zachte neon glow voor snelle herkenning.

---

## ?? Architectuur

Het project gebruikt een modulair ontwerp zodat onderdelen eenvoudig uitbreidbaar zijn.

### ?? TechnologieÎn
- **Node.js** backend  
- **Express** voor API-routes  
- **PostgreSQL** voor opslag en queries  
- **Fuse.js** voor fuzzy matching  
- **Calibre-Web** en **Kavita** voor media  
- **Docker Compose** voor orchestratie  
- **ngrok** of **Nginx Proxy Manager** voor externe toegang  
- **Slack API** voor slash-commands en bots  

### ?? Microservices / Containers
- `slack-postcodebot`
- `slack-adresbot`
- `calibre-web`
- `kavita`
- `pg-container` (PostgreSQL)
- `dashboard` (front-end)

---

## ?? Illustratie

Hieronder een moderne flat-stijl illustratie van het dashboardconcept:

*(voeg hier de gegenereerde afbeelding toe in GitHub)*  
```markdown
![Dashboard Voorbij Illustratie](./illustratie.png)

?? Installatie
1. Repo clonen
git clone https://github.com/stefanv2/dashboard-voorbij.git
cd dashboard-voorbij

2. .env aanmaken

Voor bijvoorbeeld database-connectie, Slack tokens, etc.

3. Docker opstarten
docker compose up -d

4. Dashboard openen

Browser ? http://<host>:<port>

?? Configuratie
PostgreSQL

Importeer je adresdata of andere tabellen:

CREATE DATABASE postcode;
\c postcode

-- Voorbeeld: KTB_PCDATA import
COPY ktb_pcdata
FROM '/import/ktb_pcdata.csv'
WITH (FORMAT csv, HEADER true);

Slack integratie

Configureer Slash Commands

Geef je ngrok of NPM-endpoint op

Voeg tokens toe aan .env

?? Toekomstige plannen

Integratie met LLM-agent voor slimme vragen

Historie van zoekopdrachten

Notificatiesysteem

Meer kaartvisualisaties (Google Maps / OSM)

Integratie met Jellyfin dashboards

Widget-system met drag & drop

Donkere en lichte themaís

????? Over

Dit dashboard is gebouwd als persoonlijk project:
een centrale plek waar hobby, data en automatisering samenkomen.
Praktisch, snel, visueel aantrekkelijk ó en vooral leuk om dagelijks te gebruiken.

?? Licentie

MIT License.