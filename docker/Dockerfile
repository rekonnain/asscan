FROM kalilinux/kali-rolling

ADD . /app

RUN apt update && && DEBIAN_FRONTEND=noninteractive apt install -y apt-utils; \
DEBIAN_FRONTEND=noninteractive apt install -y \
git xvfb xdotool bc phantomjs imagemagick python3-pip apt-utils \
nmap masscan expect curl; \
DEBIAN_FRONTEND=noninteractive apt -y install golang; \
go get github.com/ffuf/ffuf

# install metasploit
RUN curl -s https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > /tmp/msfinstall; \
chmod 755 /tmp/msfinstall; \
 /tmp/msfinstall

RUN cd /app && make python
WORKDIR /app/asscan
CMD ["python3", "/app/asscan/server.py"]
