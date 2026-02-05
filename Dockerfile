# Dockerfile for Therefore Configuration Processor

# Use official Python base image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install the package with AI features and curl for health checks
RUN apt-get update && apt-get install -y curl && \
    pip install --no-cache-dir -e ".[webai]"

# Create output directory
RUN mkdir -p /app/output

# Expose the web server port
EXPOSE 5050

# Health check - verify the web server is running
HEALTHCHECK --interval=30s --timeout=3s \
    CMD curl -f http://localhost:5050/ || exit 1

# Default command - run the web server
CMD ["python", "-m", "src.web"]
