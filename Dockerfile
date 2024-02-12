FROM kalilinux/kali-rolling
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update ; apt-get -y install metasploit-framework ; apt-get -y install enum4linux
RUN apt-get -y install golang; go install github.com/ffuf/ffuf/v2@latest; cp /root/go/bin/ffuf /usr/local/bin
RUN apt-get -y install python3-pip xvfb xdotool bc imagemagick python3-tornado masscan expect rdesktop crackmapexec
RUN pip3 install --break-system-packages vncdotool; pip3 install --break-system-packages webscreenshot
RUN mkdir ass
COPY install-phantomjs.sh ass/
RUN cd ass; bash install-phantomjs.sh
RUN apt-get -y install npm
RUN npm i -g yarn
RUN npm i --unsafe-perm -g wappalyzer
# wappalyzer depends on something, not sure what, it's a browser so let's solve it by brute force
RUN apt-get -y install $(apt-cache depends chromium | grep Depends | grep -v desktop-portal-backend | sed "s/.*ends:\ //" | tr '\n' ' ')
RUN apt-get -y install freerdp2-x11 smbmap
RUN apt-get -y install python3-venv; python3 -m pip install --break-system-packages pipx
RUN pipx ensurepath
RUN mkdir resources
ADD common.py notes.py results.py scheduler.py server.py log.py reporting.py scanners.py scrapers.py autosslrdp.exp helpers.py ass/
ADD RDP-screenshotter.sh ass/
ADD resources/quickhits.txt ass/resources/
ADD ui /ass/ui
ADD scanners /ass/scanners
COPY ./flag.txt /root/flag.txt
RUN mkdir -p /ass/results
RUN chmod +x ./ass/server.py
CMD [ "sh", "-c",  "cd ass;./server.py 8888 0.0.0.0" ]
