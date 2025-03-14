# Use official Python image as base
FROM python:3.10

# Set the working directory
WORKDIR /app

# Copy the project files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt


# Expose the Django port
EXPOSE 8000

CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:8000 backend.wsgi:application"]

