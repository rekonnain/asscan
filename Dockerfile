FROM kalilinux/kali-rolling
RUN apt-get update ; apt-get -y install metasploit-framework
RUN apt-get -y install golang; go get github.com/ffuf/ffuf; cp /root/go/bin/ffuf /usr/local/bin
RUN apt-get -y install python3-pip xvfb xdotool bc imagemagick python3-tornado masscan expect rdesktop
RUN pip3 install vncdotool; pip3 install webscreenshot
RUN mkdir ass
COPY install-phantomjs.sh ass/
RUN cd ass; bash install-phantomjs.sh
RUN apt-get -y install npm
RUN npm -g config set user root
RUN npm install -g npm
RUN npm i --unsafe-perm -g wappalyzer
# wappalyzer depends on something, not sure what, it's a browser so let's solve it by brute force
RUN apt-get -y install $(apt-cache depends chromium | grep Depends | sed "s/.*ends:\ //" | tr '\n' ' ')
RUN mkdir resources
ADD common.py notes.py results.py scheduler.py server.py log.py reporting.py scanners.py scrapers.py autosslrdp.exp helpers.py ass/
ADD RDP-screenshotter.sh ui ass/
ADD resources/quickhits.txt ass/resources/
ADD ui /ass/ui
ADD scanners /ass/scanners
RUN chmod +x ./ass/server.py
