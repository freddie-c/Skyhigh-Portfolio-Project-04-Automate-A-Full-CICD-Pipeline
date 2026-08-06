# Base: slim = Debian minus build toolchain; smaller attack surface
FROM python:3.11-slim

# Pinned UID/GID 10001 so the K8s securityContext can reference it by number
RUN addgroup --system --gid 10001 appgroup \
    && adduser --system --uid 10001 --ingroup appgroup appuser

# All relative paths below resolve from here
WORKDIR /app

# Deps manifest alone, so the pip layer caches independently of code changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code last: editing app.py doesn't invalidate the pip layer above
COPY app.py .

# Drop privileges BEFORE the app runs
USER appuser

# Documentation only; publishes nothing by itself
EXPOSE 5001

# Exec form: gunicorn becomes PID 1 and receives SIGTERM on rolling updates
# --access-logfile - sends logs to stdout so kubectl logs can read them
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "2", "--access-logfile", "-", "app:app"]