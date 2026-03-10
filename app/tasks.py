import os
import socket
import ipaddress
from celery import Celery
import psycopg2
import requests
from urllib.parse import urlparse

from fastapi import HTTPException
from models import AnalyzeRequest

celery = Celery(
    'tasks',
    broker=os.getenv('CELERY_BROKER_URL'),
    backend=os.getenv('CELERY_RESULT_BACKEND')
)
db_url = os.getenv('DATABASE_URL')

def is_private_ip(url):
    try:
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname or url
        ip_str = socket.gethostbyname(hostname)
        ip = ipaddress.ip_address(ip_str)
        if ip.is_private:
            return True
    except Exception as e:
        return True

    return False

@celery.task(name='tasks.analyze_url', bind=True, max_retries=3)
def analyze_url(self, url: str):
    status_code = None
    response_ms = None
    try:
        if is_private_ip(url):
            status_code = 403
            return

        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, timeout=5, headers=headers)
        status_code = response.status_code
        response_ms = int(response.elapsed.total_seconds() * 1000)
    except requests.exceptions.RequestException as e:
        print(f"Error analyzing {url}: {e}")
        raise self.retry(exc=e, countdown=2 ** self.request.retries)
    finally:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO url_results (url, status_code, response_ms) VALUES (%s, %s, %s)",
            (url, status_code, response_ms)
        )
        conn.commit()
        cur.close()
        conn.close()


def analyze_urls(request: AnalyzeRequest):
    if len(request.urls) > 10:
        raise HTTPException(status_code=400, detail="Äläpä pistele kymmentä enempää näitä. Mun CPU ei pysty händlää tätä")

    urls = [url for url in request.urls if url.lower(
    ).startswith(("http://", "https://"))]

    for url in urls:
        celery.send_task('tasks.analyze_url', args=[url])
    return {"queued": len(urls)}


def get_urls_json():
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    cur.execute(
        "SELECT id, url, status_code, response_ms, processed_at FROM url_results")

    rows = cur.fetchall()
    urls = [{"id": row[0], "url": row[1], "status_code": row[2],
             "response_ms": row[3], "processed_at": row[4]} for row in rows]

    cur.close()
    conn.close()

    return {"urls": urls}
