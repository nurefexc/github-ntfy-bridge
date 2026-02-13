FROM python:3.11-alpine
LABEL authors="nurefexc"

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application script
COPY main.py .

# Create data directory for SQLite database
RUN mkdir -p /app/data

# Set default environment variables
ENV SYNC_INTERVAL=300
ENV TZ=Europe/Budapest

# Run the application
CMD ["python", "main.py"]
