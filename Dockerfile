# Build stage
FROM python:3.9-slim as builder

WORKDIR /app

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.9-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.9/site-packages/ /usr/local/lib/python3.9/site-packages/

# Copy application code
COPY . .

# Make port 8080 available
EXPOSE 8080

# Start the app with explicit error reporting
CMD exec python -u app.py 2>&1