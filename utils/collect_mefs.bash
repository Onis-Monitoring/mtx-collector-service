#!/bin/bash

DATE=$1
SUBDOMAIN=$2

ssh -i /etc/mef-publishing-ssh-secret/ssh-privatekey mtxdepmef@10.237.30.88 /bin/bash << EOF

ls -la /opt/matrixx/mef/NOD00"${SUBDOMAIN}"/ | grep "${DATE}"

EOF