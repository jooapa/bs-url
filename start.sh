#!/bin/bash

until psql postgresql://user:password@postgres:5432/urlchecker -c '\q' 2>/dev/null; do
  sleep 1
done

psql postgresql://user:password@postgres:5432/urlchecker <<EOF
CREATE TABLE IF NOT EXISTS url_results (
  id SERIAL PRIMARY KEY,
  url TEXT NOT NULL,
  status_code INTEGER,
  response_ms INTEGER,
  processed_at TIMESTAMP DEFAULT NOW()
);
EOF

uvicorn main:app --host 0.0.0.0 --port 8000 &

celery -A tasks worker --loglevel=info