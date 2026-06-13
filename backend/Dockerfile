FROM python:3.11-slim

# Install uv using the official pre-compiled binaries
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install FastAPI and Uvicorn explicitly using uv to system python environment
RUN uv pip install --system --no-cache fastapi uvicorn

# Copy application source code (though overridden in development by docker-compose volume mounts)
COPY app/ app/

# Expose backend port
EXPOSE 8000

# Start application using uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
