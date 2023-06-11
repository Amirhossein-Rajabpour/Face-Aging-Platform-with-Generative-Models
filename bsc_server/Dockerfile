# Use official Python runtime as a parent image
FROM python:3.10-slim-buster

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt .

# Install the dependencies from the requirements file
RUN pip install -r requirements.txt

# Copy the rest of the application code to the container
COPY . .

# Start the Django server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"] 
