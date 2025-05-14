#Python 3.10.2
#Required packages:
#pip install -U python-dotenv
#pip install -U requests
import getpass
import base64
import os
import requests
from requests.auth import HTTPBasicAuth
from urllib.parse import urljoin, urlparse
import json
from dotenv import load_dotenv

#use the .env file
load_dotenv()
#ignore warnings from urllib
requests.packages.urllib3.disable_warnings() 

username = os.getenv('username')
password = os.getenv("password")
ip = os.getenv("ip")

#make the basic auth token
bAuth = base64.b64encode(bytes(f"{username}:{password}", 'utf-8'))
bAuth = bAuth.decode("utf-8")
bHead = f"Basic {bAuth}"
header = {"Authorization" : bHead}

#SHOULD define version query string for REST compatibility, but leaving off for this demo 
#version = "?ver=15.1.8"

#define html output file
f = open("index.html",'w')
print("<!DOCTYPE html>\n<html>\n<title>GTM Status</title>\n<body>\n", file=f)
print("<h1>F5 GTM Status Page</h1>", file=f)

#WideIP list is in in https://{{bigip}}/mgmt/tm/gtm/wideip/a/
# /a/ is <type> for all objects - all objects are likely A, so not iterating types in this script
wideResponse = requests.get(f"https://{ip}/mgmt/tm/gtm/wideip/a/", verify=False, headers=header)
jsonWide = wideResponse.json()

for wideip in jsonWide['items']:
  print("<h2>WideIP: " + wideip['name'] + "</h2>", file=f)
  
  if "pools" in wideip:
    for pool in wideip['pools']:
        poolLink = pool['nameReference']['link'].replace("localhost",ip)
        poolResponse = requests.get(poolLink, verify=False, headers=header)
        jsonPool = poolResponse.json()
        #pool availiblity is in in https://{{bigip}}/mgmt/tm/gtm/pool/a/~<partition>~<pool_name>/stats
        pStatsSextuple = urlparse(poolLink)
        pStatsUrl = (pStatsSextuple.scheme + "://" + pStatsSextuple.hostname + pStatsSextuple.path + "/stats")
        pStats = requests.get(pStatsUrl, verify=False, headers=header).json()
        pStatus = "<font color=\"blue\"> Unknown </font>"
                
        #the status objects are a key/value inside of a dict inside of a dict inside of a json
        for value in pStats['entries'].values():
          for v2 in value.values():

            if v2['entries']['status.availabilityState'].get('description') == "available":
              print("<h3><img src=\"up-icon.png\" alt=\"up\">", file=f)
              pStatus = "<font color=\"green\"> Enabled </font>"
            elif v2['entries']['status.enabledState'].get('description') == "disabled":
              print("<h3><img src=\"disabled-icon.png\" alt=\"disabled\">", file=f)
              pStatus = "<font color=\"grey\"> Disabled : </font>" + v2['entries']['status.statusReason'].get('description')
            elif v2['entries']['status.availabilityState'].get('description') == "offline":
              print("<h3><img src=\"down-icon.png\" alt=\"disabled\">", file=f)
              pStatus = "<font color=\"red\"> Offline : </font>" + v2['entries']['status.statusReason'].get('description')
            else:
              pStatus = pStatus
            
          print("GTM Pool : " + jsonPool['name'] + " ---> " + pStatus + "</h3>", file=f)
        
        #member availiblity is in https://{{bigip}}/mgmt/tm/gtm/pool/a/~<partition>~<pool_name>/members/stats
        membersLink = jsonPool['membersReference']['link'].replace("localhost",ip)
        membersSextuple = urlparse(membersLink)
        #memberReference link always has a ver= query string, this removes that to add the /stats path
        membersUrl = (membersSextuple.scheme + "://" + membersSextuple.hostname + membersSextuple.path + "/stats")
        membersResponse = requests.get(membersUrl, verify=False, headers=header)
        jsonMembers = membersResponse.json()

        #the status objects are a key/value inside of a dict inside of a dict inside of a json
        for value in jsonMembers['entries'].values():
          for v2 in value.values():
            print("<p> --> Member: <b>" +  v2['entries']['vsName'].get('description') + "</b>", file=f)
            print(" [GSLB Server: " +  v2['entries']['serverName'].get('description') + "]<br/>", file=f)
            print("  --> " + v2['entries']['status.enabledState'].get('description') + "<br/>", file=f)
            print("  --> " + v2['entries']['status.availabilityState'].get('description'), file=f)
            print(" : Reason: " + v2['entries']['status.statusReason'].get('description'), file=f)
    
  print("</p>\n<hr>\n", file=f)

print("</body>\n</html>", file=f)
