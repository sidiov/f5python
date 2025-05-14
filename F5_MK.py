#Python 3.11
#pip install requests
import sys
import requests
from requests.auth import HTTPBasicAuth
import base64
import json
import os.path
import ipaddress
from datetime import datetime

###############
####Vars**********
###############
#we should define version for REST
f5version = "?ver=17.0.0"
FILE = "servers.txt"
pFILE = ".a"
dt = datetime.now().strftime("%m-%d-%Y")
sFILE = (f'{dt}-mk.txt')

#this disables warnings on the big-ip management cert (ie self-signed/expired)
requests.packages.urllib3.disable_warnings() 

###############
####Functions******
###############

#validate a string as IP and handle the ValueError
def validate_ip(ip_str):
    try:
        ip = ipaddress.ip_address(ip_str)
        return True
    except ValueError:
        return False
    
###############
####Main***********
###############
try:
    with open(FILE) as file:
        bigips = [line.rstrip() for line in file]
except IOError:
    print(f"Could not read file: {FILE}")
    sys.exit(2)

try:
    with open(pFILE) as f:
        mylist = f.read().splitlines() 
        password = mylist[0]
except IOError:
    print(f"Could not read file: {pFILE}")
    sys.exit(2)

bAuth = base64.b64encode(bytes(f"admin:{password}", 'utf-8'))
bAuth = bAuth.decode("utf-8")
bHead = f"Basic {bAuth}"
header = {
    "Authorization": bHead,
    "Content-Type": "application/json",
    "Cache-Control": "no-cache"
}
data = { "command":"run", "utilCmdArgs":"-c 'f5mku -K'" }


for ip in bigips:
    if not validate_ip(ip):
        print("Could not validate {ip}.")
        continue

    response = requests.post(f"https://{ip}/mgmt/tm/util/bash", json=data, verify=False, headers=header)
    jr = response.json()

    try:
        with open(sFILE, mode='a', encoding="utf-8") as f:
            f.write(f"{ip}: {jr['commandResult']}\r\n")
    except IOError:
        print(f"Could not open file: {sFILE}")
        sys.exit(2)