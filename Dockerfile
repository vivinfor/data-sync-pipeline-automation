# Base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install system dependencies for psycopg2, netcat-openbsd and other requirements
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Add wait-for-it script to wait for PostgreSQL to be ready
RUN curl -o /wait-for-it.sh https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh
RUN chmod +x /wait-for-it.sh

# Copy project files
COPY . /app

# Install dependencies (including system packages)
RUN pip install --no-cache-dir -r requirements.txt

# Expose the Django development server port
EXPOSE 8000

# Run the Django development server, waiting for DB to be ready
CMD ["./wait-for-it.sh", "db:5432", "--", "python", "manage.py", "runserver", "0.0.0.0:8000"]
