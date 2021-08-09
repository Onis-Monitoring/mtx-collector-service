SUBDOMAIN=$1

ssh -i /etc/mef-publishing-ssh-secret/ssh-privatekey mtxdepmef@10.237.30.88 /bin/bash << EOF

ls -la /opt/matrixx/mef/NOD00"${SUBDOMAIN}"/ | grep mef_* | wc -l

EOF