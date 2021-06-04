# flask_web/app.py

import subprocess
import json
import os
import platform
import threading
import time
import xml.etree.ElementTree as ET
import requests

import logging

from datetime import datetime
from calendar import timegm
from flask import Flask, request, g, jsonify, make_response
from flask_cors import CORS, cross_origin
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import make_wsgi_app, Summary, Info, Gauge
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily, REGISTRY
from datetime import date
from settings import METRIC_1, METRIC_2, METRIC_3, METRIC_4, PRICING_STATUS, MEF_LOG_FILE, PATH_TO_MEF_BACKLOG, MEF_LOG_FILE_NAME, MEF_LOG_FILE_PATH, SNMP_ADRESS, SUBDOMAINS, ENGINES, REPLICAS, EVENT_REPOSITORY_LOADER
from time import mktime
from snmp_service import get_engine_status

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

def convert_to_time_ms(timestamp):
    return 1000 * timegm(
            datetime.strptime(
                timestamp, '%Y-%m-%dT%H:%M:%S.%fZ').timetuple())


def create_data_event_repository(start, end, length=2):
    proc = subprocess.check_output(["print_event_repository_loader_trace.py", "-g", "-u", "MtxAdmin", "--host=mongo-0.mongo.mongodb.svc.cluster.local:27017"])

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
                    print('correct in files: {} and {}'.format(old_line, line.strip()))
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
    while subdomain <= SUBDOMAINS:
        engine = 1
        while engine <= ENGINES:
            replica = 0
            tmp_time = 0.0
            tmp_path = ''
            snmp_add = SNMP_ADRESS.format(subdomain, engine)
            isActive = get_engine_status(engine, snmp_add)
            print('Subdomain {} Engine {} status: {}'.format(subdomain, engine, isActive['id']))
            #Encontrar engine activo
            if isActive['id'] == 8:
                print('isActive[] == 8')
                while replica <= (REPLICAS - 1):
                    PATH = MEF_LOG_FILE_PATH.format(subdomain, engine, replica, MEF_LOG_FILE_NAME)
                    print('PATH {}'.format(PATH))
                    try:
                        stat = os.stat(PATH)
                        print('STAT {}'.format(stat))
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
        subdomain += 1

def getMefBackLog():
    subdomain = 1
    PATH = ''
    while subdomain <= SUBDOMAINS:
        engine = 1
        while engine <= ENGINES:
            replica = 0
            snmp_add = SNMP_ADRESS.format(subdomain, engine)
            isActive = get_engine_status(engine, snmp_add)
            print('Subdomain {} Engine {} status: {}'.format(subdomain, engine, isActive['id']))
            #Encontrar engine activo
            if isActive['id'] == 8:
                print('isActive[] == 8')
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
        subdomain += 1

@app.route("/testPath")
@cross_origin()
def testPath():
    # return getActivePublishingBlade()
    # return glob.glob(PATH_TO_MEF_BACKLOG + '*.log')
    # print('testPath')
    # logger.debug("Querying the Status of Engine")
    # snmp_add = SNMP_ADRESS.format(1, 1)
    # print('SNMP_ADRESS:')
    # print(snmp_add)
    # isActive = get_engine_status(1, snmp_add)
    # print('STATUS:')
    # print(isActive)
    #getActivePublishingBlade()

    #31-05-2021
    # getMefBackLog()
    

    return make_wsgi_app()

@app.route("/")
@cross_origin()
def index():
    return "OK"

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
    # try:
    #     with open(MEF_LOG_FILE,'r') as fp:
    #         line = fp.readline()
    #         counter = 0
    #         old_line = 'something'
    #         send_alert = False
    #         alerted_files = []
    #         while line:
    #             if '.xml.gz' in line.strip():
    #                 formatted = line.strip().replace('.', '_').split('_')
    #                 if counter == 0:
    #                     counter = formatted[3]
    #                 elif (int(counter) + 1) == int(formatted[2]):
    #                     print('correct in files: {} and {}'.format(old_line, line.strip()))
    #                     counter = formatted[3]
    #                 else:
    #                     send_alert = True
    #                     alerted_files.append(line.strip())
    #                     print('There is a gap between: {} and {}'.format(old_line, line.strip()))
    #                     counter = formatted[3]
    #                 old_line = line.strip()
    #             line = fp.readline()
    #         if send_alert:
    #             print("Sending to prometheus")
    #             dictMetric = {}
    #             c = 1
    #             for mef in alerted_files:
    #                 dictMetric['file_{}'.format(c)] = mef
    #                 c += 1
    #             METRIC_2.info(dictMetric)
    #         else:
    #             METRIC_2.info({'file_1': ''})
            
    # except Exception as e:
    #     logger.error(e)
    #     print(e)
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
