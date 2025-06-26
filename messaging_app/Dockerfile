# Use python as base
FROM python:3.13-slim
# Install required system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    gcc \
    && rm -rf /var/lib/apt/lists/*
# create app directory
RUN mkdir /app

# Set working directory inside the box
WORKDIR /app

# Copy requirements.txt and install packages
COPY Requirements.txt /app/
RUN pip install --no-cache-dir -r Requirements.txt

# copy django app code
COPY . /app/

# Expose port 8000 - default django port
EXPOSE 8000

# Start django server when box runs
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
CMD ["sh", "-c", "echo '-p 8000'; python manage.py runserver 0.0.0.0:8000"]
