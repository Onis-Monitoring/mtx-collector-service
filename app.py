# flask_web/app.py

import subprocess
import json
import os
import requests
import logging
import glob

from datetime import datetime
from flask import Flask
from flask import request
from flask_cors import CORS, cross_origin
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import make_wsgi_app
from settings import METRIC_1, METRIC_2, METRIC_3, METRIC_4,METRIC_5, METRIC_6, METRIC_7, METRIC_8, PRICING_STATUS, MEF_LOG_FILE,\
PATH_TO_MEF_BACKLOG, MEF_LOG_FILE_NAME, MEF_LOG_FILE_PATH, SNMP_ADRESS, SUBDOMAINS, REPLICAS,\
EVENT_REPOSITORY_LOADER,PATH_CHECKPOINT,ENGINE,CHECKPOINT_TIME, ENGINES
from time import mktime

import socket,time,sys 
from timeit import default_timer as timer
#from snmp_service import get_engine_status

app = Flask(__name__)
cors = CORS(app)

logger = logging.getLogger(__name__)

app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.config['Access-Control-Allow-Origin'] = '*'
app.config['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
app.config['Access-Control-Allow-Headers'] = \
        'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

# Add prometheus wsgi middleware to route /metrics requests
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

def process_mef_file_log(file, subdomain):
    with open(file,'r') as fp:
        print('Processing {} mef file...'.format(file))
        line = fp.readline()
        counter = 0
        old_line = 'something'
        send_alert = False
        alerted_files = []
        while line:
            if '.xml.gz' in line.strip():
                formatted = line.strip().replace('.', '_').split('_')
                if counter == 0:
                    counter = formatted[3]
                elif (int(counter) + 1) == int(formatted[2]):
                    # print('correct in files: {} and {}'.format(old_line, line.strip()))
                    counter = formatted[3]
                else:
                    send_alert = True
                    alerted_files.append(line.strip())
                    print('There is a gap between: {} and {}'.format(old_line, line.strip()))
                    counter = formatted[3]
                old_line = line.strip()
            line = fp.readline()
        if send_alert:
            print("Sending to prometheus")
            dictMetric = {}
            c = 1
            for mef in alerted_files:
                dictMetric['file_{}'.format(c)] = mef
                c += 1
            dictMetric['subdomain'] = str(subdomain)
            METRIC_2[subdomain-1].info(dictMetric)
        else:
            METRIC_2[subdomain-1].info({'file_1': '', 'subdomain': str(subdomain)})

def getActivePublishingBlade():
    subdomain = 1
    PATH = ''
    # while subdomain <= SUBDOMAINS:
    for subdomain in SUBDOMAINS:
        engine = ENGINE
        while engine <= ENGINES:
            replica = 0
            tmp_time = 0.0
            tmp_path = ''
            snmp_add = SNMP_ADRESS.format(subdomain, engine)
            #isActive = get_engine_status(engine, snmp_add)
            isActive = {"id": 8}
            print('Subdomain {} Engine {} status: {}'.format(subdomain, engine, isActive['id']))
            #Encontrar engine activo
            if isActive['id'] == 8:
                while replica <= (REPLICAS - 1):
                    PATH = MEF_LOG_FILE_PATH.format(subdomain, engine, replica, MEF_LOG_FILE_NAME)
                    print('PATH {}'.format(PATH))
                    try:
                        stat = os.stat(PATH)
                        # print('STAT {}'.format(stat))
                        try:
                            validTime = mktime(datetime.now().timetuple()) - stat.st_mtime
                            if (tmp_time != 0.0) & (tmp_time < validTime):
                                print('Found mef_file in: {}'.format(tmp_path))
                                process_mef_file_log(tmp_path, subdomain)
                            elif (tmp_time != 0.0) | (REPLICAS == 1):
                                print('Found mef_file in: {}'.format(PATH))
                                process_mef_file_log(PATH, subdomain)

                            # if validTime <= 60*60*24:

                            tmp_time = validTime
                            tmp_path = PATH
                        except AttributeError:
                            print(e)
                        # return PATH
                    except Exception as e:
                        print(e)
                        PATH = ''
                    replica += 1
            engine += 1
        # subdomain += 1

def getMefBackLog():
    # subdomain = 1
    PATH = ''
    for subdomain in SUBDOMAINS:
        engine = ENGINE
        while engine <= ENGINES:
            replica = 0
            snmp_add = SNMP_ADRESS.format(subdomain, engine)
            #isActive = get_engine_status(engine, snmp_add)
            isActive = {"id": 8}
            print('Subdomain {} Engine {} status: {}'.format(subdomain, engine, isActive['id']))
            #Encontrar engine activo
            if isActive['id'] == 8:
                # print('isActive[] == 8')
                while replica <= (REPLICAS - 1):
                    PATH = PATH_TO_MEF_BACKLOG.format(subdomain, engine, (replica + 1))
                    print('PATH {}'.format(PATH))
                    try:
                        files = os.listdir(PATH)
                        backlog = False
                        for file in files:
                            if '.xml.gz' in file:
                                path = '{}{}'.format(PATH, file)
                                stat = os.stat(path)
                                backlog = True if mktime(datetime.now().timetuple()) - stat.st_mtime > 120 else False
                                print('Backlog status {}'.format(backlog))
                                if backlog:
                                    break
                        METRIC_1[replica].info({'backlog_status': str(backlog)})  
                    except Exception as e:
                        print(e)
                    replica += 1
            engine += 1

@app.route("/testPath")
@cross_origin()
def testPath():
    return make_wsgi_app()

@app.route("/")
@cross_origin()
def index():
    return "OK"

@app.route("/api/checkInterSiteLatency", methods=['GET'])
@cross_origin()
def checkInterSiteLatency():

    remote_host = request.args.get('remoteHost')
    remote_port = request.args.get('remotePort')
    timeout = request.args.get('timeout')

    if timeout is None:
        max_latency=15
    else:    
        max_latency= int(timeout)

    message="get cluster_state 0001-16f5bd2d"

    sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(max_latency)
    sock.sendto(message,(remote_host,int(remote_port)))

    try:

        data,address=sock.recvfrom(4096)

        # If response is received before max latency, set latency as 0 latency; meaning inter connectivity test is OK.
        METRIC_8.set(0)

    except:

        # If something goes wrong, set latency to max_latency value; meaning inter connectivity test failed.
        METRIC_8.set(max_latency)

    # If something goes wrong, set latency to max_latency value; meaning inter connectivity test failed.
    METRIC_8.set(max_latency)

    # Return latency value.
    return make_wsgi_app() 

    

@app.route("/api/checkPricing")
@cross_origin()
def check_pricing_status():
    reason = 'Not Found'
    try:
        proc= requests.get(PRICING_STATUS, verify=False, timeout=5)
        if proc.reason:
            reason = proc.reason
        json_res = json.loads(proc.text)
        print(json_res['IsActivePricing'])

        # x = 1 if json_res['IsActivePricing'] == True else 0

        METRIC_3.info({'version': str(json_res['MaxSysSchemaVersion']), 'status': str(json_res['IsActivePricing'])})
    except Exception as e:
        print(e)
        METRIC_3.info({'reason': reason, 'status': str(False)})

    return make_wsgi_app()

@app.route("/api/checkMefGaps")
@cross_origin()
def check_mef_gaps():
    print("Executing checkMefGaps method")
    logger.debug("Executing checkMefGaps method logger")
    getActivePublishingBlade()

    return make_wsgi_app()

@app.route("/api/checkMefBacklog")
@cross_origin()
def check_mef_backlog():
    try:
        getMefBackLog()
    except Exception as e:
        print(e)
    
    return make_wsgi_app()

@app.route("/api/checkEventLoadRepo")
@cross_origin()
def check_event_loader():
    result = subprocess.check_output(EVENT_REPOSITORY_LOADER)
    lines = result.splitlines()
    dictMetric = {}
    send_alert = False
    missing_ranges = False
    c = 1
    for line in lines:
        if 'Sub-domain' in line:
            dictMetric['subdomain'] = str(line)
        if 'GTC ranges are missing' in line:
            missing_ranges = True
        if ('- ' in line) & missing_ranges:
            send_alert = True
            dictMetric['range_{}'.format(c)] = line
            c += 1
    if send_alert:
        print("Sending to prometheus")
        METRIC_4.info(dictMetric)
    else:
        METRIC_4.info({'range_1': ''})
    return make_wsgi_app()

@app.route("/api/checkLastCheckpointing")
@cross_origin()
def check_last_checkpointijng():
    # subdomain = 1
    PATH = ''
    # while subdomain <= SUBDOMAINS:
    for subdomain in SUBDOMAINS:
        try:
            engine = ENGINE
            send_alert = False
            PATH = PATH_CHECKPOINT.format(subdomain)
            full_path = glob.glob(PATH)
            if full_path:
                files = os.listdir(full_path[0])
                result = filter(lambda x: 'ckpt' in x, files)
                sort_result = sorted(result)
                full_path = '{}{}'.format(PATH, sort_result[-1])
                stat = os.stat(full_path)
                valid_time = mktime(datetime.now().timetuple()) - stat.st_mtime
                send_alert = valid_time > CHECKPOINT_TIME
                print(send_alert)
                METRIC_5[subdomain-1].info({'valid': str(send_alert),'subdomain':str(subdomain), 'path':str(full_path[0]) })
            # subdomain += 1
        except Exception as e:
            print(e)

    return make_wsgi_app()

@app.route("/api/validateCheckpointErrors")
@cross_origin()
def validate_checkpoint_errors():
    for subdomain in SUBDOMAINS:
        try:
            # engine = ENGINE
            errors = 0
            # engine_name = 's{}e{}'.format(subdomain,engine)
            engine_name = 's{}e'.format(subdomain)
            proc = subprocess.check_output(["kubectl", "get", "--sort-by=.metadata.creationTimestamp", "pods"])
            lines = [line for line in proc.splitlines() if 'validate' in line and engine_name in line]
            if lines:
                splitline = [l for l in lines[-1].split(' ') if l != '']
                if splitline and 'validate' in splitline[0]:
                    command =  ["kubectl", "logs", "-c", "validatecheckpoint", splitline[0]]
                    print(command)
                    proc2 = subprocess.check_output(command)
                    if 'Errors=' in proc2:
                        errors = int(proc2.split()[2].split('=')[1])
            METRIC_6[subdomain-1].set(errors)
        except Exception as e:
            print(e)

    return make_wsgi_app()

@app.route("/api/validateMefDestination")
@cross_origin()
def validate_mefs_destination():
    try:
        proc = subprocess.check_output(["bash", "collect_processing_files.bash"])
        lines = proc.splitlines()
        for i, line in enumerate(lines):
            print(line)
            # line = '-rwxrwxr-x 1 mtxdepmef mtxdepmef 57 2021-07-03 06:56:48.628752148 -0500 /opt/matrixx/mef/NOD003/PublishProgress.engine_2'
            time = ' '.join([l for l in line.split(' ') if l != ''][5:7])
            final = mktime(datetime.now().timetuple()) - mktime(datetime.strptime(time.split('.')[0], "%Y-%m-%d %H:%M:%S").timetuple()) > 120
            values = [l for l in line.split(' ') if l != ''][-1].split('/')[-2:]

            METRIC_7[i].info({'status': str(final),'node':values[0], 'file':values[1] })
    except Exception as e:
        print(e)

    return make_wsgi_app()
   
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
