from easysnmp import snmp_get, EasySNMPError 
from logger import logger
 
OID = '.1.3.6.1.4.1.35838.1.1.1.1.2.5.1.3.%d.1'
ENGINE_STATUSES = {
    '0': {'name': 'Unknown', 'id': 0},
    '1': {'name': 'Start', 'id': 1},
    '2': {'name': 'Pre-Init', 'id': 2},
    '3': {'name': 'Init', 'id': 3},
    '4': {'name': 'Post-Init', 'id': 4},
    '5': {'name': 'Standby-Sync', 'id': 5},
    '6': {'name': 'Standby', 'id': 6},
    '7': {'name': 'Active-Sync', 'id': 7},
    '8': {'name': 'Active', 'id': 8},
    '9': {'name': 'Backstop', 'id': 9},
    '10': {'name': 'Exit', 'id': 10},
    '11': {'name': 'Stop', 'id': 11},
    '12': {'name': 'Final', 'id': 12},
    '13': {'name': 'Failed', 'id': 13},
    '14': {'name': 'None', 'id': 14}
}
UNKNOWN_ENGINE_STATUS = ENGINE_STATUSES['0']
ACTIVE_ENGINE_STATUS = ENGINE_STATUSES['8']
 
logger = logger()
 
def get_engine_status(engine_id, snmp_address, cluster_id = 1):
 
    try:
        logger.debug("Querying the Status of Engine {}".format(engine_id))
        oid = ".1.3.6.1.4.1.35838.1.1.1.1.2.5.1.3.{}.{}".format(engine_id, cluster_id)
        logger.info("SNMP Query {} on {}".format(oid, snmp_address))
        var = snmp_get(oid, hostname=snmp_address, community='public', version=2)
        logger.debug("Engine {} State is {}".format(engine_id, var.value))
 
        # Look up the Engine Status
        engine_status = ENGINE_STATUSES[str(var.value)]
        if not engine_status:
            logger.warn("Unable to lookup Engine Status using {}. Reverting to status Unknown".format(var.value))
            engine_status = UNKNOWN_ENGINE_STATUS
 
    except Exception as exception:
        logger.warn("Could not determine the Status of Engine {}: {}".format(engine_id, exception))
        engine_status = UNKNOWN_ENGINE_STATUS
 
    logger.info("The status of Engine {} is {}".format(engine_id, engine_status['name']))
 
    return engine_status
