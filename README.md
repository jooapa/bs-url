# URL Checker

- Kaikki palvelut pyörivät omassa Docker-kontissaan.
- FastAPI tarjoaa REST-rajapinnan, joka vastaanottaa URL:it ja antaa ne yksitellen Celerylle tarkistettavaksi.
- Celery-taskissa tehdään tarkistus ja tulos tallennetaan PostgreSQL-tietokantaan.

- Projekti käyttää:
    - Python 3.12 
      - *Dockerissakin on python:3.12-slim, koska tämä projekti ei tarvitse ylimääräistä roskaa, jota normaalin Pythonin mukana tulee* 
    - FastAPI    - ***REST API***
    - Celery     - ***Taustatyöt***
    - Redis      - ***Celeryn broker, joka välittää tehtävät Celerylle***
    - PostgreSQL 16 - ***Tietokanta***
    - uvicorn    - ***Rajapinta FastAPI:lle, jota se tarvitsee***

## URL-analyysi
Kun Celery saa URL:n, Python tekee HTTP-pyynnön kyseiseen osoitteeseen ja mittaa vasteajan sekä statuskoodin. Python ei myöskään hyväksy, jos URL:eja on 10 tai enemmän.

### Virheiden käsittely
- Jos URL-merkkijono ei ala "http://" tai "https://", se heitetään pois eikä sitä tarkisteta.
- Jos nettisivu ei vastaa, Python yrittää uudestaan 2^(yritysten määrä) sekunnin kuluttua.
- Jos URL on yksityinen IP-osoite, sille annetaan statuskoodiksi 403, eikä sitä tarkisteta.

## Käyttö

Tarvitset toimivan Linux-koneen, johon on asennettu Docker ja docker-compose. Sitten voit ajaa komennon:
```sh
docker-compose up --build
# tai
docker compose up --build
```
## API

```json
- POST /analyze
    - Body:  '{"urls": ["http://jooapa.com"]}'
    - Vastaa: {"queued": 1}

- GET /urls
    - Vastaa: {"urls": [
        {
            "id": 1,
            "url": "http://jooapa.com",
            "status_code": 200,
            "response_ms": 1292,
            "processed_at": "2026-03-09T18:46:29.779520"
        }, ...
    ]}
```

### Testit

```sh
curl -X POST "http://localhost:8000/analyze" -H "Content-Type: application/json" -d '{"urls": ["http://jooapa.com"]}'
# > {"queued":1}

curl -X GET "http://localhost:8000/urls"
# > {"urls": [
# >     {
# >         "id": 1,
# >         "url": "http://jooapa.com",
# >         "status_code": 200,
# >         "response_ms": 1292,
# >         "processed_at": "2026-03-09T18:46:29.779520"
# >     }, ...
```

## AI

AI:ta on käytetty projektin arkkitehtuurin suunnittelussa, docker-composen kirjoittamisessa, Python-koodin aloituksessa ja virheiden korjaamisessa. Työkaluna käytettiin Copilotia.

## Turvallisuus

Ympäristömuuttujia on käytetty `.env`-tiedostossa. *"En nyt pistänyt .env-tiedostoa .gitignoreen yksinkertaisuuden vuoksi, mutta sinne se todellisuudessa kuuluisi."*

Docker-composessa myös tietokannan, Celeryn ja Rediksen URL:it on määritelty ympäristömuuttujina.

SQL-injektioiden ei pitäisi olla mahdollisia, koska käytän SQL-komennossa turvallista parametrisointia, joka käsittelee arvot turvallisesti [tasks.py](./app/tasks.py#L52)-tiedostossa.

## Enemmän aikaa

Jos minulla olisi enemmän aikaa, lisäisin projektille testit (yksikkö- ja integraatiotestit), URL-tarkistuksen priorisoinnin sekä käyttöliittymän (esim. Reactilla), jossa voisi helposti syöttää URL:eja ja tarkastella niiden tuloksia.
