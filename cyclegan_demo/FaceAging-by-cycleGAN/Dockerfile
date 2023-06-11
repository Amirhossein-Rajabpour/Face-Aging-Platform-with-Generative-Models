# Use official Python runtime as a parent image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Upgrade pip
RUN pip install pip==23.1.2

# Copy the requirements file to the container
COPY requirements.txt .

# Install the dependencies from the requirements file
RUN pip install -r requirements.txt --no-cache-dir

# Install Flask
RUN pip install flask

# Copy the rest of the application code to the container
COPY . .

# Create following directories
RUN mkdir -p ./datasets/y2o/testA/
RUN mkdir -p ./datasets/y2o/testB/
RUN mkdir -p ./checkpoints/aging_cyclegan/

# Copy the pre-trained model
# RUN cp ./trained_model/1_wiki_base_mix/latest_net_G_A.pth ./checkpoints/aging_cyclegan/latest_net_G.pth

RUN cp ./trained_model/1_wiki_base_mix/latest_net_G_A.pth ./checkpoints/aging_cyclegan/latest_net_G_A.pth
RUN cp ./trained_model/1_wiki_base_mix/latest_net_G_B.pth ./checkpoints/aging_cyclegan/latest_net_G_B.pth

# Run the flask server
CMD ["python", "server.py"]