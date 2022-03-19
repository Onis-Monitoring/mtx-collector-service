ssh -i /etc/mef-publishing-ssh-secret/ssh-privatekey mtxdepmef@10.237.30.88 /bin/bash << EOF

ls --full-time -lrt /opt/matrixx/SnapShotDaily/SSD001/ | tail -n 1

EOF