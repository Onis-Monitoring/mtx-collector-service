ssh -i /etc/ssh/ssh-privatekey mtxdepmef@10.237.30.88 /bin/bash << EOF

ls --full-time /opt/matrixx/SnapShotDaily/SSD001/ | tail -n 1

EOF