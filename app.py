# flask_web/app.py
import math
import subprocess
import json
import os
import platform
import sys
import threading
import time
import re
import xml.etree.ElementTree as ET
import requests

from datetime import datetime
from calendar import timegm
from flask import Flask, request, g, jsonify, make_response
from flask_cors import CORS, cross_origin
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import make_wsgi_app, Summary, Info, Gauge
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily, REGISTRY
from datetime import date
from settings import METRIC_1, METRIC_2, METRIC_3, PRICING_STATUS, MEF_LOG_FILE, PATH_TO_MEF_BACKLOG

app = Flask(__name__)
cors = CORS(app)

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


@app.route("/")
@cross_origin()
def index():
    return "OK"

@app.route("/api/checkPricing")
@cross_origin()
def check_pricing_status():
    try:
        proc= requests.get(PRICING_STATUS, verify=False, timeout=5)
        json_res = json.loads(proc.text)
        print(json_res['IsActivePricing'])

        x = 1 if json_res['IsActivePricing'] == True else 0

        METRIC_3.info({'version': str(json_res['MaxSysSchemaVersion']), 'status': str(json_res['IsActivePricing'])})
    except Exception as e:
        print(e)
        METRIC_3.info({'version': 'Not Found', 'status': str(False)})

    return make_wsgi_app()

@app.route("/api/checkMefGaps")
@cross_origin()
def check_mef_gaps():
    try:
        with open(MEF_LOG_FILE,'r') as fp:
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
                METRIC_2.info(dictMetric)
    except Exception as e:
        print(e)

    return make_wsgi_app()

@app.route("/api/checkMefBacklog")
@cross_origin()
def check_mef_backlog():
    try:
        if platform.system() == 'Windows':
            date1 = False if datetime.now().timestamp() - os.path.getctime(PATH_TO_MEF_BACKLOG) > 10 else True
            print('date1 : {}'.format(date1))
        else:
            stat = os.stat(PATH_TO_MEF_BACKLOG)
            try:
                date1 = False if datetime.now().timestamp() - stat.st_birthtime > 160 else True
                print('time: {}'.format(date1))
            except AttributeError:
                date1 = False if datetime.now().timestamp() - stat.st_mtime > 160 else True
                print('time: {}'.format(date1))
        METRIC_1.info({'path': PATH_TO_MEF_BACKLOG, 'status': str(date1)})
    except Exception as e:
        print(e)
    
    return make_wsgi_app()

@app.route("/api/checkEventLoadRepo")
@cross_origin()
def check_event_loader():
    return make_wsgi_app()

class MEFFileBacklogThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.board = 1

    def run(self):
        i = Gauge('mef_file_backlog_status', 'Description of pricing', ['method', 'path'])
        while True:
            if platform.system() == 'Windows':
                date1 = 1 if datetime.now().timestamp() - os.path.getctime(path_to_file) > 60 else 0
                i.labels(method='get', path=path_to_file).set(date1)
            else:
                stat = os.stat(path_to_file)
                
                try:
                    date1 = 1 if datetime.now().timestamp() - stat.st_birthtime > 60 else 0
                    i.labels(method='get', path=path_to_file).set(date1)
                except AttributeError:
                    # We're probably on Linux. No easy way to get creation dates here,
                    # so we'll settle for when its content was last modified.
                    date1 = 1 if datetime.now().timestamp() - stat.st_mtime > 60 else 0
                    i.labels(method='get', path=path_to_file).set(date1)
            time.sleep(60)
    
    def stop(self):
        self._stop.set()

backlogThread = MEFFileBacklogThread()


if __name__ == '__main__':
    # backlogThread.start()
    app.run(debug=True, host='0.0.0.0')
