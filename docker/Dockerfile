FROM kalilinux/kali-rolling

ADD . /app

RUN apt update && DEBIAN_FRONTEND=noninteractive apt install -y \
git xvfb xdotool bc phantomjs imagemagick python3-pip apt-utils; \
DEBIAN_FRONTEND=noninteractive apt -y install golang; \
go get github.com/ffuf/ffuf

RUN cd /app && make python
WORKDIR /app/asscan
CMD ["python3", "/app/asscan/server.py"]
