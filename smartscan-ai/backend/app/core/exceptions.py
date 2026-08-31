class SmartScanError(Exception): pass
class DataLeakageError(SmartScanError): pass
class MetadataError(SmartScanError): pass
class ReceiverError(SmartScanError): pass
class PolicyError(SmartScanError): pass
