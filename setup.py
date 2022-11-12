#!/usr/bin/python
from __future__ import print_function
import subprocess
import os
print("[*] Installing requirements.txt")
subprocess.Popen("pip3 install -r requirements.txt", shell=True).wait()
print("[*] Installing mksec to /usr/share/mksec")
print(os.getcwd())
subprocess.Popen("mkdir /usr/share/mksec/;mkdir /etc/mksec/;cp -rf * /usr/share/mksec/;cp src/core/config.baseline /etc/mksec/mksec.config", shell=True).wait()
print("[*] Creating launcher for mksec...")
filewrite = open("/usr/local/bin/mksec", "w")
filewrite.write("#!/bin/sh\ncd /usr/share/mksec\n./mksec")
filewrite.close()
print("[*] Done. Chmoding +x")
subprocess.Popen("chmod +x /usr/local/bin/mksec", shell=True).wait()
print("[*] Finished. Run 'mksec' to start the MKSecurity.")
