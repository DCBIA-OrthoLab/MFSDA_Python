FROM python:3.9

WORKDIR /app

RUN apt-get update && apt-get install -y \
	libx11-6 \
	libgl1 \
	libopengl0 \
	libegl1 

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN git clone https://github.com/DCBIA-OrthoLab/MFSDA_Python.git