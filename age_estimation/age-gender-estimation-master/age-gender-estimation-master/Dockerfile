# Use official Python runtime as a parent image
FROM python:3.6.9

# Set the working directory in the container
WORKDIR /app

# Upgrade pip
# RUN pip install pip==23.1.2

# Install tensorflow
RUN pip install tensorflow==2.3.0

# Copy the requirements file to the container
COPY requirements.txt .

# Install the dependencies from the requirements file
RUN pip install -r requirements.txt --no-cache-dir

# Install Flask
RUN pip install flask

# Copy the rest of the application code to the container
COPY . .

# Run the flask server
CMD ["python", "server.py"]