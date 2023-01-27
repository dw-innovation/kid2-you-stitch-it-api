FROM ubuntu:20.04

ENV TZ=Africa/Cairo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    python3.8-minimal \
    python3-pip \
 && rm -rf /var/lib/apt/lists/*

EXPOSE 5000

WORKDIR /app

COPY requirements.txt ./requirements.txt

RUN pip3 install --no-cache-dir -r requirements.txt

COPY app .

CMD ["flask", "run", "--host=0.0.0.0"]
