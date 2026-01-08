FROM node:20-alpine AS frontend_build
WORKDIR /frontend

COPY frontend/package.json ./package.json
RUN npm install
COPY frontend/. ./
RUN npm run build


FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1

# Run as non-root
RUN useradd -m -u 10001 appuser \
	&& mkdir -p /data \
	&& chown -R appuser:appuser /data

# Default to a writable sqlite location inside the container
ENV DATABASE_URL=sqlite+aiosqlite:////data/calendar.db

COPY app/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -q -r requirements.txt

# Code backend (package "app") + assets statiques legacy
COPY app ./app
COPY static ./static

# Frontend v2 build (Vite dist) servi par FastAPI
COPY --from=frontend_build /frontend/dist ./v2_dist

USER appuser

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--access-log", "--log-level", "info"]
