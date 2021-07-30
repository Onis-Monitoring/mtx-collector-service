from prometheus_client import Summary, Info, Gauge

# Metrics Definition
METRIC_1 = [Info('mef_file_backlog_status_1', 'Description of mef backlog'), Info('mef_file_backlog_status_2', 'Description of mef backlog')]
METRIC_2 = [Info('mef_gap_file1', 'Description of mef gaps sub1'), Info('mef_gap_file2', 'Description of mef gaps sub2'), Info('mef_gap_file3', 'Description of mef gaps sub3')]
METRIC_3 = Info('pricing_status', 'Description of pricing')
METRIC_4 = Info('event_repository_loader', 'Event Repository Loader Ranges')
METRIC_5 = [Info('checkpointing_status_1','checkpointing generation date'),Info('checkpointing_status_2','checkpointing generation date'),Info('checkpointing_status_3','checkpointing generation date')]
METRIC_6 = [Gauge('checkpointing_errors_1','validate checkpoint errors'),Gauge('checkpointing_errors_2','validate checkpoint errors'),Gauge('checkpointing_errors_3','validate checkpoint errors')]
METRIC_7 = [Info('destination_status_1','mef destination status'),Info('destination_status_2','mef destination status'),Info('destination_status_3','mef destination status'), Info('destination_status_4','mef destination status'), Info('destination_status_5','mef destination status'), Info('destination_status_6','mef destination status')]
METRIC_8 = [Gauge('checkpointing_warnings_1','validate checkpoint warning'),Gauge('checkpointing_warnings_2','validate checkpoint warnings'),Gauge('checkpointing_warnings_3','validate checkpoint warnings')]

PRICING_STATUS = 'http://rsgateway-ag1:8080/rsgateway/data/json/pricing/status'

# MEF_LOG_FILE = r'D:\Trabajo\Onis\Monitoring\Monitoring_v2\grafana-python-datasource-master\grafana-python-datasource-master\flask\publish_mefs.log'
MEF_LOG_FILE = r'/etc/prometheus/publish_mefs.log'
MEF_LOG_FILE_PATH = r'/mnt/shared-logging-storage-s{0}e{1}/publ-s{0}e{1}-{2}/{3}'
# MEF_LOG_FILE_PATH = r'/etc/prometheus/shared-logging-storage-s{0}e{1}/publ-s{0}e{1}-{2}/{3}'
MEF_LOG_FILE_NAME = 'publish_mefs.log'
# PATH_TO_MEF_BACKLOG = r'/etc/prometheus/publish_mefs.log'
# PATH_TO_MEF_BACKLOG = r'./publish_'
PATH_TO_MEF_BACKLOG = r'/mnt/fast-shared-storage-s{0}e{1}/local_{1}_2_{2}/staging/mef_temp'
PATH_CHECKPOINT = r'/mnt/shared-storage-s{0}e*/checkpoints/'

ERL_USER = "MtxAdmin"
ERL_HOST = "--host=10.237.3.143"
# ERL_HOST = "--host=mongo-0.mongo.mongodb.svc.cluster.local"
EVENT_REPOSITORY_LOADER = ["print_event_repository_loader_trace.py", "-g", "-u", ERL_USER, ERL_HOST]

SNMP_ADRESS = 'publ-cls-s{}e{}:4700'

SUBDOMAINS = [1,2,3]
ENGINES = 2
REPLICAS = 2
ENGINE = 1
CHECKPOINT_TIME=5400

PRICING_STATUS_JSON_MOCK = {
    "$": "MtxResponsePricingStatus",
    "ActivateTime": "2021-04-13T18:12:20.880162-05:00",
    "CreateLoginId": "henrique",
    "Domain": "ATTMex_5212_v0",
    "IsActivePricing": False,
    "MaxServiceProviderSchemaVersion": 15,
    "MaxSysSchemaVersion": 5212,
    "ModifiedTime": "2021-04-09T08:53:36.815000-05:00",
    "Repository": "file:///var/mtx_catalog_builder/repo/ATTMex_5212_v0",
    "Result": 0,
    "ResultText": "OK",
    "Rev": 100,
    "RouteId": 1,
    "_resultCode": 0,
    "_resultText": "OK",
    "_resultType": "get"
}