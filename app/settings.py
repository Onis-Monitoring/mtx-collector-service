import os
from prometheus_client import Summary, Info, Gauge, Counter

# Metrics Definition
METRIC_1 = [Info('mef_file_backlog_status_1', 'Description of mef backlog'), Info('mef_file_backlog_status_2', 'Description of mef backlog')]
METRIC_2 = [Info('mef_gap_file1', 'Description of mef gaps sub1'), Info('mef_gap_file2', 'Description of mef gaps sub2'), Info('mef_gap_file3', 'Description of mef gaps sub3')]
METRIC_3 = Info('pricing_status', 'Description of pricing')
METRIC_4 = Info('event_repository_loader', 'Event Repository Loader Ranges')
METRIC_5 = [Info('checkpointing_status_1','checkpointing generation date'),Info('checkpointing_status_2','checkpointing generation date'),Info('checkpointing_status_3','checkpointing generation date')]
METRIC_6 = [Gauge('checkpointing_errors_1','validate checkpoint errors'),Gauge('checkpointing_errors_2','validate checkpoint errors'),Gauge('checkpointing_errors_3','validate checkpoint errors')]
METRIC_7 = [Info('destination_status_1','mef destination status'),Info('destination_status_2','mef destination status'),Info('destination_status_3','mef destination status'), Info('destination_status_4','mef destination status'), Info('destination_status_5','mef destination status'), Info('destination_status_6','mef destination status')]
METRIC_8 = [Gauge('checkpointing_warnings_1','validate checkpoint warning'),Gauge('checkpointing_warnings_2','validate checkpoint warnings'),Gauge('checkpointing_warnings_3','validate checkpoint warnings')]
METRIC_9 = Gauge('inter_site_latency', 'Inter site connectivity latency measure')
METRIC_10 = [Gauge('mefs_1','number of mefs in sftp'),Gauge('mefs_2','number of mefs in sftp'),Gauge('mefs_3','number of mefs in sftp')]
METRIC_11 = Info('inter_site_trace_path', 'Inter site connectivity trace path')
METRIC_12 = Info('mtx_valid_snapshot', 'Daily snapshot check')
METRIC_13 = Gauge('mtx_snapshot_time', 'Daily snapshot time')
METRIC_14 = Counter('http_api_response_time_count', 'http_api_response_time_count')
METRIC_15 = Counter('http_api_response_time_sum', 'http_api_response_time_sum')
# METRIC_14 = [Gauge('mtx_volume_space_1','volume space used in percentage'),Gauge('mtx_volume_space_2','volume space used in percentage'),Gauge('mtx_volume_space_3','volume space used in percentage')]

PRICING_STATUS = 'http://rsgateway-ag1:8080/rsgateway/data/json/pricing/status'

LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')
MEF_LOG_FILE_PATH = r'/mnt/shared-logging-storage-s{0}e{1}/publ-s{0}e{1}-{2}/{3}'
MEF_LOG_FILE_NAME = 'publish_mefs.log'
PATH_TO_MEF_BACKLOG = r'/mnt/fast-shared-storage-s{0}e{1}/local_{1}_2_{2}/staging/mef_temp'
PATH_CHECKPOINT = r'/mnt/shared-storage-s{0}e*/checkpoints/'

ERL_USER = "MtxAdmin"
ERL_HOST = "--host=10.237.3.143"
# ERL_HOST = "--host=mongo-0.mongo.mongodb.svc.cluster.local"
EVENT_REPOSITORY_LOADER = ["print_event_repository_loader_trace.py", "-g", "-u", ERL_USER, "--host={}".format(ERL_HOST)]

SNMP_ADRESS = 'publ-cls-s{}e{}:4700'

SUBDOMAINS = int(os.getenv('SUBDOMAINS', 3))
ENGINES = int(os.getenv('ENGINES', 2))
REPLICAS = int(os.getenv('REPLICAS', 2))
ENGINE = 1
CHECKPOINT_TIME= int(os.getenv('CHECKPOINT_TIME', 5400))
SNAPSHOT_TIME= int(os.getenv('SNAPSHOT_TIME', 87000)) # 1d 10 min