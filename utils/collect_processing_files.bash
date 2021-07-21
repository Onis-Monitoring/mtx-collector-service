ssh -i /etc/mef-publishing-ssh-secret/ssh-privatekey mtxdepmef@10.237.30.88 /bin/bash << EOF

ls --full-time /opt/matrixx/mef/NOD00*/PublishProgress.engine*

EOF