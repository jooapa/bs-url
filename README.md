# URL Checker

- Kaikki palvelut pyörii omassa docker kontissa.
- FastAPI tarjoaa REST:in, joka vastaanottaa URL:it ja antaa ne yksitellen Celerylle tarkistettavaksi.
- Celery taskissa tehdään tarkistus ja tulos tallennetaan postgreSQL tietokantaan.

- Projekti käyttää:
    - Python 3.12 
      - *Dockerikin on python:3.12-slim, koska tää projari ei tarvitse lisä roskaa mitä tulee normaalin pythonin mukana* 
    - FastAPI    - ***REST API***
    - Celery     - ***Taustatyöt***
    - Redis      - ***Celeryn broker, joka välittää tehtävät Celerylle***
    - PostgreSQL 16 - ***Tietokanta***
    - uvicorn    - ***Rajapinta FastAPI:lle, jota se tarvitsee***

## URL Analyysi
Kun Celery saa URL:in, Python tekee HTTP pyynnön kyseiseen URL:iin ja mittaa vasteajan sekä statuskoodin. Python ei hyväksy myöskään jos urlia on 10 tai enemmän.

### Virheiden käsittely
- Jos URL string ei ala "http://" tai "https://", se heitetään pois, ja sitä ei tarkisteta.
- Jos nettisivu ei vastaa, python yrittää uudestaan 2^(yrityksen määrän) sekunnin päästä
- Jos URL on yksityinen IP-osoite, Sille annetaan status koodiksi 403, eikä sitä tarkisteta.

## Käyttö

Pitää olla asennettuna toimina linux boksin, jossa on docker ja docker-compose. Ja sitten vain ajaa komento:
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

### Testi Curlei

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

AI:ta on käytetty projektin arkkitehtuurin suunnittelussa, composen kirjoittamisessa ja Pythonissa startti riveihin, josta voin helposti jatkaa ja todellakin virheiden korjaamisessa. Käytin Copilotia

## Turvallisuus

On käytetty ympäristömuuttujia `.env` tiedostossa. *"en nyt pistänyt yksinkertaisuuden vuoksi gitignoreen, mutta sinne se kuuluisi"*

docker-composessa on myös tietokannan, celeryn ja rediksen urlit ympäristömuuttujina.

Ei pitäisi olla myös mahdollista mikään SQL injektiokaan kun käytän sql komennossa values parametriä, joka pistää sen literaalisen stringin arvoon [tasks.py](./app/tasks.py#L28):ssä

## Enemmän aikaa

Jos minulla olisi enemmän aikaa, lisäisin testit (unit ja integraatiot), URl-tarkistuksen priorisointi, käyttöliittymä esim. Reactilla, jossa pystyisi helposti kirjoittamaan urlia ja nähdä niitä.
