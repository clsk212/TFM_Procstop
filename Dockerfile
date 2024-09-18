# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.12.0
FROM python:${PYTHON_VERSION}-slim AS base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

# Set PYTHONPATH to include /app directory to ensure all modules are found
ENV PYTHONPATH=/app

WORKDIR /app

# Create a non-privileged user that the app will run under.
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# Crear el directorio analytics y asegurarse de que los permisos sean correctos
RUN mkdir -p /app/analytics && chown -R appuser:appuser /app

# Copy the source code into the container
COPY . .
COPY . /app


# Cambiar a usuario no privilegiado
USER appuser

# Expose the port that the application listens on
EXPOSE 8000

# Run the application
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app.app:app"]
