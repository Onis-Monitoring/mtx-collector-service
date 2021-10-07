import subprocess
import logging
import logging.config
import logging.handlers
import os

filename='last_gtc.log'
logger = logging.getLogger('test')
path = os.path('/home/mtx/gunicorn/evet_loader/')
handler = logging.handlers.RotatingFileHandler(path+filename, maxBytes=200000, backupCount=1)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)

result = subprocess.check_output(['print_event_repository_loader_trace.py','-g','-u', 'MtxAdmin','--host=10.237.3.143'])

newResult = result.splitLine()

newReult2 = newResult[4].split()

# for word in newReult2:
#     try:
#         lastGTC = int(word)
#         break
#     except:
#         pass

lastGTC = [w for w in newReult2 if w.isdigit()]

print(lastGTC)

if lastGTC:
    logger.info(lastGTC)

