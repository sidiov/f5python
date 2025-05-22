#Python 3.11
#pip install requests
#pip install argparse
import sys
import getpass
import base64
import argparse
import requests
import ipaddress
from requests.auth import HTTPBasicAuth
from urllib.parse import urlsplit, urlunsplit
import json
import os.path
from datetime import datetime

####Vars**********
#we should define version for REST
f5version = "?ver=17.0.0"
bigips = None
ip = None
DEBUG = False
FILE = None

#this disables warnings on the big-ip management cert (ie self-signed/expired)
requests.packages.urllib3.disable_warnings() 

####functions***********
#log if debug set
def dlog(msg):
    if DEBUG:
        print(msg)
    return

def outMsg(FILE, msg):
    if FILE is None:
        print(msg)
    else:
        with open(FILE, mode='a', encoding="utf-8") as f:
            f.write(f"{msg}\n")
    return

#create basic auth token
def aToken(username, password):
    bAuth = base64.b64encode(bytes(f"{username}:{password}", 'utf-8'))
    bAuth = bAuth.decode("utf-8")
    bHead = f"Basic {bAuth}"
    header = {"Authorization" : bHead}
    return header

#remove the query from url (easier to build)
def url_clean(url):
  # Split the URL into its components
  # url_parts.scheme, .netloc, .path, 
  url_parts = urlsplit(url)

  return f"{url_parts.path}"

#convert object names for api url format
def urlApiName(object):
  new_name = object.replace('/','~') 
  return new_name

def getF5Url(host, uri):
    response = requests.get(f"https://{host}{uri}{f5version}", verify=False, headers=header)
    dlog(f"{uri} => {response}")
    return response.json()

#validate a string as IP and handle the ValueError
def validate_ip(ip_str):
    try:
        ip = ipaddress.ip_address(ip_str)
        return True
    except ValueError:
        return False

def getTCPProfiles(bigip):

    return

####Main***********
argParser = argparse.ArgumentParser()
argParser.add_argument("-b", "--bigip", type=str, help="BIG-IP host")
argParser.add_argument("-u", "--username", type=str, help="BIG-IP user")
argParser.add_argument("-p", "--password", type=str, help="BIG-IP pass")

args = argParser.parse_args()
print("args=%s" % args)

if args.bigip is None:
    print("Device IP or name: ", end="")
    bigip = input()

if args.username is None:
    print("Username: ", end="")
    username = input()
    
if args.password is None:
    password = getpass.getpass()

if bigip is not None:
    #create the basic auth token
    header = aToken(username, password)
