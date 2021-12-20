#!/usr/bin/env python
# -*- coding: utf-8 -*-

#bunlar henuz yuklenmedi
#sudo apt install skipfish -y
#sudo apt install bulk_extractor -y

import os
os.system("echo '\x1b[1m\033[36m>>Installation Started...\x1b[0m\033[0m'")
#tools
os.system("sudo apt-get update -y; sudo apt install git -y; sudo apt install pip -y; sudo apt install dmitry -y; sudo apt install ike-scan -y;sudo apt install netdiscover -y; sudo apt install nbtscan -y; sudo apt install nmap -y; sudo apt install nikto -y; sudo apt install chkrootkit -y; sudo apt install lynis -y; sudo apt install sqlmap -y; sudo apt install cewl -y; sudo apt install crunch -y; sudo apt install hashcat -y; sudo apt install john -y; sudo apt install medusa -y; sudo apt install ncrack -y; sudo apt install hashid -y; sudo apt install macchanger -y; sudo apt install weevely -y; sudo apt install binwalk -y; sudo apt install hashdeep -y; sudo apt install foremost -y; sudo apt install cutycapt -y; sudo apt-get install -y dsniff")
#for wpscan
os.system("sudo apt-get install libcurl4-openssl-dev libxml2 libxml2-dev libxslt1-dev ruby-dev build-essential libgmp-dev zlib1g-dev -y")
os.system("sudo apt install ruby-full -y")
os.system("sudo gem install wpscan")
#for metasploit
os.system("sudo apt install -y ruby ruby-dev build-essential zlib1g zlib1g-dev libpq-dev libpcap-dev libsqlite3-dev")
os.system("sudo git clone https://github.com/rapid7/metasploit-framework /opt/metasploit-framework")
os.system("cd /opt/metasploit-framework && sudo gem install bundler")
os.system("cd /opt/metasploit-framework && sudo bundle install")
#for searchsploit
os.system("sudo git clone https://github.com/offensive-security/exploitdb.git /opt/exploitdb")
os.system("sudo ln -sf /opt/exploitdb/searchsploit /usr/local/bin/searchsploit")
#for responder
os.system("sudo git clone https://github.com/lgandx/Responder.git /opt/Responder")
#for exe2hex
os.system("sudo git clone https://github.com/g0tmi1k/exe2hex.git /opt/exe2hex")
#for pipal
os.system("sudo git clone https://github.com/digininja/pipal.git /opt/pipal")
#for unix-privesc-check
os.system("sudo git clone https://github.com/pentestmonkey/unix-privesc-check.git /opt/unix-privesc-check")

#simply add mksec a folder in your $PATH variable
os.system("sudo cp mksec.py /usr/bin/mksec")
#os.system("sudo cp mksec.py /usr/local/bin/mksec")
os.system("sudo chmod 755 /usr/bin/mksec")
#os.system("sudo chmod 755 /usr/local/bin/mksec")

#for theharvester 
os.system("pip3 install aiodns aiohttp shodan aiosqlite ujson netaddr uvloop aiomultiprocess")
os.system("sudo git clone https://github.com/laramies/theHarvester /opt/theHarvester")
os.system("python3 -m pip install -r requirements/base.txt")
#for veil
os.system("sudo git clone https://github.com/Veil-Framework/Veil.git /opt/Veil")
os.system("cd /opt/Veil && sudo ./config/setup.sh --force --silent")

os.system("clear")
os.system("echo '\x1b[1m\033[36m>>Installation Complete...\x1b[0m\033[0m'")
os.system(quit())