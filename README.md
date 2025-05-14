# f5python
Terrible python for F5 stuff

**F5Cert_v1.py** - Iterate the Virtuals to find SSL profiles and the certs they contain, output names and dates to csv format.  You can do this for ALL certs easily in the API, but to find actual in-use certs requires more.

**F5_MK.py** - Grab and save Master Keys from a list of servers.  Useful if you are automating backups, although the MK should not generally change, there are cases where it may not be the same as it was previously. 

**F5_GTMStats** - Super simple example for a GTM up down WIP/Pool status page.
