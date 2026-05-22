FROM ghcr.io/astral-sh/uv:python3.11-alpine

WORKDIR /app

# Projektabhängigkeiten synchronisieren (nutzt die uv.lock / pyproject.toml)
COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen

# Restlichen Code kopieren
COPY . .

# Wir lassen den Container offen, die Befehle feuern wir über docker-compose ab