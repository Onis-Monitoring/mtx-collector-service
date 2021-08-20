import socket,time,sys 
from timeit import default_timer as timer
 
ip="10.237.31.215"
port=4800
message='get cluster_state #0001-16f5bd2d'
 
sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.settimeout(5)
 
while True:
  sock.sendto(message,(ip,port))
  start=timer()
  try:
    data,address=sock.recvfrom(4096)
    elapsed=timer()-start
    print ('%s %.3f'%(data,elapsed*1000))
  except:
    print ('Timed out after 5 seconds')
  sys.stdout.flush()
  time.sleep(1)
