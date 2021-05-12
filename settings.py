from prometheus_client import Summary, Info, Gauge

METRIC_1 = Info('mef_file_backlog_status', 'Description of mef backlog')
METRIC_2 = Info('mef_gap_file', 'Description of mef gaps')
METRIC_3 = Info('pricing_status', 'Description of pricing')

PRICING_STATUS = 'https://matrixx-rsgw.mx.att.com/rsgateway/data/json/pricing/status'

# MEF_LOG_FILE = r'D:\Trabajo\Onis\Monitoring\Monitoring_v2\grafana-python-datasource-master\grafana-python-datasource-master\flask\publish_mefs.log'
MEF_LOG_FILE = r'/etc/prometheus/publish_mefs.log'

PATH_TO_MEF_BACKLOG = r'/etc/prometheus/publish_mefs.log'
# PATH_TO_MEF_BACKLOG = r'./publish_mefs.log'

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