FROM python:3.12-slim

WORKDIR /app

# psycopg2-binary needs libpq at runtime on slim images
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Most container platforms (Cloud Run, Render, Railway, App Runner)
# inject the port to listen on via $PORT; default to 8000 for hosts
# that don't (e.g. a plain `docker run` or AWS ECS with a fixed
# container port).
ENV PORT=8000
EXPOSE 8000

# Runs migrations (including all seed data) before starting the
# server, same as the Procfile — whichever entrypoint mechanism a
# given host actually uses, both do the same thing.
CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
