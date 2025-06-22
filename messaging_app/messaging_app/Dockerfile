# Use python as base
FROM python:3.10

# Set working directory inside the box
WORKDIR /app

# Copy requirements.txt and install packages
COPY Requirements.txt .
RUN pip install --no-cache-dir -r Requirements.txt

# copy django app code
COPY . .

# Expose port 8000 - default django port
EXPOSE 8000

# Start django server when box runs
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
