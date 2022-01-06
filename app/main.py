# flask_web/app.py

from app.logger import logger
import subprocess
import json
import os
import requests
import glob
import errno
import logging

from datetime import datetime
from flask import Flask
from flask import request
from flask_cors import CORS, cross_origin
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import make_wsgi_app
from settings import METRIC_1, METRIC_2, METRIC_3, METRIC_4,METRIC_5, METRIC_6, METRIC_7, METRIC_8, METRIC_9, PRICING_STATUS, MEF_LOG_FILE,\
METRIC_10, METRIC_11, METRIC_12, METRIC_13, PATH_TO_MEF_BACKLOG, MEF_LOG_FILE_NAME, MEF_LOG_FILE_PATH, SNMP_ADRESS, SUBDOMAINS, REPLICAS,\
EVENT_REPOSITORY_LOADER,PATH_CHECKPOINT,ENGINE,CHECKPOINT_TIME, ENGINES, SNAPSHOT_TIME
from time import mktime
from logger import logger, logger_intersite
import socket,time,sys 
from timeit import default_timer as timer
# from snmp_service import get_engine_status

# logger = logger()
logger = logger(__name__, logging.DEBUG)
logger_intersite = logger_intersite('intersite', logging.DEBUG)

# def get_engine_status(engine, snmp_add, test=False):
#     if not test:
#         from snmp_service import get_engine_status
#         return get_engine_status(engine, snmp_add)

#     return {'id': 8}

def create_app():
    __author__ = 'Edgar Lopez'
    __copyright__ = 'Copyright (C) 2020 Edgar Lopez'
    __license__ = 'Onis Solutions'
    __version__ = '2.0'
    __maintainer__ = 'Edgar Lopez'
    __email__ = 'edgar.lopez@onissolutions.com'
    __status__ = 'Prod'

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

    def process_mef_file_log(file, subdomain):
        with open(file,'r') as fp:
            logger.info('Processing {} mef file...'.format(file))
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
                        counter = formatted[3]
                    else:
                        send_alert = True
                        alerted_files.append(line.strip())
                        logger.info('There is a gap between: {} and {}'.format(old_line, line.strip()))
                        counter = formatted[3]
                    old_line = line.strip()
                line = fp.readline()
            if send_alert:
                logger.info("Sending to prometheus")
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
                # isActive = get_engine_status(engine, snmp_add)
                isActive = {'id': 8}
                logger.debug('Subdomain {} Engine {} status: {}'.format(subdomain, engine, isActive['id']))
                #Encontrar engine activo
                if isActive['id'] == 8:
                    while replica <= (REPLICAS - 1):
                        PATH = MEF_LOG_FILE_PATH.format(subdomain, engine, replica, MEF_LOG_FILE_NAME)
                        logger.debug('PATH {}'.format(PATH))
                        try:
                            stat = os.stat(PATH)
                            try:
                                validTime = mktime(datetime.now().timetuple()) - stat.st_mtime
                                if (tmp_time != 0.0) & (tmp_time < validTime):
                                    logger.info('Found mef_file in: {}'.format(tmp_path))
                                    process_mef_file_log(tmp_path, subdomain)
                                elif (tmp_time != 0.0) | (REPLICAS == 1):
                                    logger.info('Found mef_file in: {}'.format(PATH))
                                    process_mef_file_log(PATH, subdomain)

                                # if validTime <= 60*60*24:

                                tmp_time = validTime
                                tmp_path = PATH
                            except AttributeError:
                                logger.warn(e)
                            # return PATH
                        except EnvironmentError as e:
                            logger.warn(os.strerror(e.errno)) 
                        except Exception as e:
                            logger.info(e)
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
                # isActive = get_engine_status(engine, snmp_add)
                isActive = {'id': 8}
                logger.debug('Subdomain {} Engine {} status: {}'.format(subdomain, engine, isActive['id']))
                #Encontrar engine activo
                if isActive['id'] == 8:
                    while replica <= (REPLICAS - 1):
                        PATH = PATH_TO_MEF_BACKLOG.format(subdomain, engine, (replica + 1))
                        logger.debug('PATH {}'.format(PATH))
                        try:
                            files = os.listdir(PATH)
                            backlog = False
                            for file in files:
                                if '.xml.gz' in file:
                                    path = '{}{}'.format(PATH, file)
                                    stat = os.stat(path)
                                    backlog = True if mktime(datetime.now().timetuple()) - stat.st_mtime > 120 else False
                                    logger.info('Backlog status {}'.format(backlog))
                                    if backlog:
                                        break
                            METRIC_1[replica].info({'backlog_status': str(backlog)})  
                        except EnvironmentError as e:
                            logger.warn(os.strerror(e.errno)) 
                        except Exception as e:
                            logger.error(e)
                        replica += 1
                engine += 1

    def getFullTime(tokens):
        time = ' '.join(tokens[5:7])
        return mktime(datetime.now().timetuple()) - mktime(datetime.strptime(time.split('.')[0], "%Y-%m-%d %H:%M:%S").timetuple())


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
        logger_intersite.info("Executing checkInterSiteLatency method")
        remote_host = request.args.get('remoteHost')
        remote_port = request.args.get('remotePort')
        timeout = request.args.get('timeout')

        if timeout is None:
            max_latency=15
        else:    
            max_latency= int(timeout)

        message="get cluster_state #0001-16f5bd2d"

        # sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # sock.settimeout(max_latency)
        # sock.sendto(message,(remote_host,int(remote_port)))

        start=timer()
        try:
            proc = subprocess.check_output(["ping", "-c", "1", remote_host])
            lines = [l for l in [line for line in proc.splitlines() if 'time=' in line][0].split(' ') if 'time' in l]
            latency = float(lines[0].split('=')[1])
            # data,address=sock.recvfrom(4096)
            # elapsed=(timer()-start)*1000
            # If response is received before timeout, return the latency value
            logger_intersite.debug('Latency {}'.format(latency))
            METRIC_9.set(latency)
        except Exception as e:
            logger_intersite.error(e)
            # If something goes wrong, set latency to max_latency value; meaning inter connectivity test failed.
            METRIC_9.set(max_latency*1000)

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
            logger.info(json_res['IsActivePricing'])

            # x = 1 if json_res['IsActivePricing'] == True else 0

            METRIC_3.info({'version': str(json_res['MaxSysSchemaVersion']), 'status': str(json_res['IsActivePricing'])})
        except Exception as e:
            logger.error(e)
            METRIC_3.info({'reason': reason, 'status': str(False)})

        return make_wsgi_app()


    @app.route("/api/checkMefGaps")
    @cross_origin()
    def check_mef_gaps():
        logger.info("Executing checkMefGaps method")
        # logger.debug("Executing checkMefGaps method logger")
        getActivePublishingBlade()

        return make_wsgi_app()


    @app.route("/api/checkMefBacklog")
    @cross_origin()
    def check_mef_backlog():
        logger.info("Executing check_mef_backlog method")
        try:
            getMefBackLog()
        except Exception as e:
            logger.error(e)
        
        return make_wsgi_app()


    @app.route("/api/checkEventLoadRepo")
    @cross_origin()
    def check_event_loader():
        logger.info("Executing check_event_loader method")
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
            logger.info("Sending to prometheus")
            METRIC_4.info(dictMetric)
        else:
            METRIC_4.info({'range_1': ''})
        return make_wsgi_app()


    @app.route("/api/checkLastCheckpointing")
    @cross_origin()
    def check_last_checkpointijng():
        logger.info("Executing check_last_checkpointijng method")
        PATH = ''
        for subdomain in SUBDOMAINS:
            try:
                send_alert = False
                PATH = PATH_CHECKPOINT.format(subdomain)
                full_path = glob.glob(PATH)
                if full_path:
                    files = os.listdir(full_path[0])
                    result = filter(lambda x: 'ckpt' in x, files)
                    if result:
                        sort_result = sorted(result)
                        full_path = '{}{}'.format(full_path[0], sort_result[-1])
                        stat = os.stat(full_path)
                        valid_time = mktime(datetime.now().timetuple()) - stat.st_mtime
                        logger.info('ckpt: {}, now: {}, last_ckpt: {}'.format(full_path,str(mktime(datetime.now().timetuple())), str(stat.st_mtime)))
                        send_alert = valid_time > CHECKPOINT_TIME
                        logger.info('Send alert: {}'.format(send_alert))
                        METRIC_5[subdomain-1].info({'valid': str(send_alert),'subdomain':str(subdomain), 'path':str(full_path[0]) })
                    else:
                        METRIC_5[subdomain-1].info({'valid': str(True),'subdomain':str(subdomain), 'path':'Not found' })
                # subdomain += 1
            except Exception as e:
                logger.error(e)

        return make_wsgi_app()


    @app.route("/api/validateCheckpointErrors")
    @cross_origin()
    def validate_checkpoint_errors():
        logger.info("Executing validate_checkpoint_errors method")
        for subdomain in SUBDOMAINS:
            try:
                # engine = ENGINE
                errors = 0
                warnings = 0
                # engine_name = 's{}e{}'.format(subdomain,engine)
                engine_name = 's{}e'.format(subdomain)
                proc = subprocess.check_output(["kubectl", "get", "--sort-by=.metadata.creationTimestamp", "pods"])
                lines = [line for line in proc.splitlines() if 'validate' in line and engine_name in line]
                if lines:
                    splitline = [l for l in lines[-1].split(' ') if l != '']
                    if splitline and 'validate' in splitline[0]:
                        command =  ["kubectl", "logs", "-c", "validatecheckpoint", splitline[0]]
                        proc2 = subprocess.check_output(command)
                        if 'Errors=' in proc2:
                            errors = int(proc2.split()[2].split('=')[1])
                        if 'Warnings=' in proc2:
                            warnings = int(proc2.split()[3].split('=')[1])
                METRIC_6[subdomain-1].set(errors)
                METRIC_8[subdomain-1].set(warnings)
            except Exception as e:
                logger.error(e)

        return make_wsgi_app()


    @app.route("/api/validateMefDestination")
    @cross_origin()
    def validate_mefs_destination():
        logger.info("Executing validate_mefs_destination method")
        try:
            proc = subprocess.check_output(["bash", "collect_processing_files.bash"])
            lines = proc.splitlines()
            for i, line in enumerate(lines):
                logger.debug(line)
                # line = '-rwxrwxr-x 1 mtxdepmef mtxdepmef 57 2021-07-03 06:56:48.628752148 -0500 /opt/matrixx/mef/NOD003/PublishProgress.engine_2'
                time = ' '.join([l for l in line.split(' ') if l != ''][5:7])
                final = mktime(datetime.now().timetuple()) - mktime(datetime.strptime(time.split('.')[0], "%Y-%m-%d %H:%M:%S").timetuple()) > 120
                values = [l for l in line.split(' ') if l != ''][-1].split('/')[-2:]

                METRIC_7[i].info({'status': str(final),'node':values[0], 'file':values[1] })
        except Exception as e:
            logger.error(e)

        return make_wsgi_app()


    @app.route("/api/validateSFTPMefsNumber")
    @cross_origin()
    def validate_mefs_destination_number():
        logger.info("Executing validate_mefs_destination_number method")
        for subdomain in SUBDOMAINS:
            try:
                proc = subprocess.check_output(["bash", "mef_list_total.bash", str(subdomain)])
                logger.debug('Result {}'.format(proc))
                try:
                    files = int(proc)
                except:
                    logger.warn('Directory not found')
                    files = 0
                METRIC_10[subdomain-1].set(files)
            except Exception as e:
                logger.error(e)

        return make_wsgi_app()


    @app.route("/api/validateTracePath")
    @cross_origin()
    def validate_trace_path():
        logger_intersite.debug("Executing Trace PathMethod")
        remote_host = request.args.get('remoteHost')
        no_replay_count = 0
        try:
            start = datetime.now()
            proc = subprocess.check_output(["tracepath", "-m", "15", remote_host])
            logger_intersite.debug('tracepath time: \r\n{}'.format(datetime.now() - start))
            dict = {}
            logger_intersite.info('tracepath: \r\n{}'.format(proc))
            # proc = subprocess.check_output(["cat", '../assets/tracepath.out'])
            lines = [line for line in proc.splitlines()]
            for line in lines:
                if no_replay_count > 3:
                    break
                word = [q for q in [l for l  in line.split(' ')] if q!='']
                if 'ms' in line:
                    no_replay_count = 0
                    if len(word) > 3:
                        dict[word[1]] = word[2]
                elif 'no reply' in line:
                    no_replay_count += 1
                    dict[word[0]] = 'no reply'
                
            # logger.info(dict)

            # METRIC_11.info(dict) # commented until fix labels
        except Exception as e:
            logger_intersite.error(e)

        return make_wsgi_app()

    
    @app.route("/api/validateSnapshot")
    @cross_origin()
    def validate_snapshot():
        logger.info("Executing validate_snapshot method")

        try:
            proc = subprocess.check_output(["bash", "mef_snapshot.bash"])
            logger.debug('Result {}'.format(proc.rstrip()))
            
            # proc = 'drwxr-xr-x 2 mtxdepmef mtxdepmef 4096 2021-09-01 05:00:21.000000000 -0500 20210901\n'
            tokens = [l for l in proc.split(' ') if l != '']
            snapshot = tokens[-1]
            # time = ' '.join(tokens[5:7])
            # final = mktime(datetime.now().timetuple()) - mktime(datetime.strptime(time.split('.')[0], "%Y-%m-%d %H:%M:%S").timetuple())
            final = getFullTime(tokens)
            logger.debug('Last snapshot time {}'.format(final))


            METRIC_12.info({'status': str(final <= SNAPSHOT_TIME), 'snapshot': snapshot.rstrip()})
            METRIC_13.set(final)
        except Exception as e:
            logger.error(e)

        return make_wsgi_app()

    
    # @app.route("/api/validateVolumeSpace")
    # @cross_origin()
    # def validate_volume_space():
    #     logger.info("Executing validate_volume_space method")

    #     try:
    #         volume = '/mnt/' + request.args.get('volume')
    #         proc = subprocess.check_output(["df", "-h"])
    #         logger.debug('Result {}'.format(proc.rstrip()))

    #         # proc = '10.237.25.18:/mnt/matrixx-prod02/k8s/nfs/vols/pvc-585cb561-e3b3-4d09-8f92-791fa71e8ced  480G  213G  268G  45% /mnt/shared-logging-storage-s1e1\n'
    #         lines = [line for line in proc.splitlines() if volume in line]
    #         for subdomain in SUBDOMAINS:
    #             engine = 's'+ str(subdomain) + 'e'
    #             line = [l for l in lines if engine in l]
    #             tokens = [l for l in line[0].split(' ') if '%' in l]
    #             if tokens:
    #                 percentage = int(tokens[0][:-1])
    #                 METRIC_14[subdomain - 1].set(percentage)


    #     except Exception as e:
    #         logger.error(e)

    #     return make_wsgi_app()
    
    return app
