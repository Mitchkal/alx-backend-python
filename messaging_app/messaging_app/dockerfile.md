# Use python as base

FROM python:3.10-slim

# Set working directory inside the box

WORKDIR /app/messaging_app

# Copy requirements.txt and install packages

COPY Requirements.txt .
RUN pip install --no-cache-dir -r Requirements.txt

# copy django app code

COPY . .

# Expose port 8000 - default django port

EXPOSE 8000

# Start django server when box runs

# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

CMD ["sh", "-c", "echo '-p 8000'; python manage.py runserver 0.0.0.0:8000"]
