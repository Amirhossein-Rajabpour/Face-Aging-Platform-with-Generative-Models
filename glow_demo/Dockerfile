FROM tensorflow/tensorflow:1.8.0-py3

RUN apt update && \
    apt install -y locales cmake libsm6 libxext6 libxrender-dev && \
    locale-gen en_US.UTF-8

ENV LC_ALL=en_US.UTF-8

RUN pip install pip==20.3.4

RUN pip install --ignore-installed tqdm
RUN pip install numpy==1.18.5
RUN pip install --ignore-installed imutils==0.5.3
RUN pip install --ignore-installed opencv-python==4.3.0.36 --no-build-isolation
RUN pip install --ignore-installed dlib==19.21.0
RUN pip install flask flask_cors

WORKDIR /app

COPY ./ ./

CMD ["python", "server.py"]