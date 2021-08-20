#!/bin/bash

DATE1=$1
DATE2=$2
SUBDOMAIN=$3

ssh -i /etc/mef-publishing-ssh-secret/ssh-privatekey mtxdepmef@10.237.30.88 /bin/bash << EOF

ls -lrt --full-time /opt/matrixx/mef/NOD00"${SUBDOMAIN}"/ | egrep "(${DATE1}|${DATE2})" | cut -d"-" -f9,10 | cut -d' ' -f2,4 | sort 

EOF