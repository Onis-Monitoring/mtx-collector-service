#!/bin/bash

DATE1=$1
DATE2=$2
SUBDOMAIN=$3

ssh -i /etc/mef-publishing-ssh-secret/ssh-privatekey mtxdepmef@10.237.30.88 /bin/bash << EOF

ls -la /opt/matrixx/mef/NOD00"${SUBDOMAIN}"/ | egrep "(${DATE1}|${DATE2})"

EOF