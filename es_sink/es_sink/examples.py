import flushing_buffer
from descriptor import ESDescriptor
from es_transport import ESTransport


################################################################################
# Example connecting to localhost with http auth
LOCALHOST_ESDESCRIPTOR = ESDescriptor("https://localhost:9200/", es_v7=True, 
                                      es_index='logs', timestamped=True, 
                                      signed=False, http_auth=('admin', 'admin'))

buffer = flushing_buffer.flushing_buffer_factory(LOCALHOST_ESDESCRIPTOR,
                                                 flush_trigger=1)

buffer.add_log_line('{"field1": "value1", "field2": "value2"}')

raw_transport = ESTransport(LOCALHOST_ESDESCRIPTOR)
result = raw_transport.send('get', "https://localhost:9200/logs*/_search")
print(result)


################################################################################
# Example connecting to Amazon Elasticsearch Service with signed requests

AMAZON_ES_ENDPOINT = "https://your endpoint here"
AMAZON_ES_DESCRIPTOR = ESDescriptor(AMAZON_ES_ENDPOINT, es_v7=True,
                                    es_index='logs', signed=True,
                                    region='us-west-2', timestamped=True)

buffer2 = flushing_buffer.flushing_buffer_factory(AMAZON_ES_DESCRIPTOR,
                                                 flush_trigger=1)

print('Sending 1 doc to Amazon ES')
buffer2.add_log_line('{"field1": "value1", "field2": "value2"}')

print('Searching')
raw_transport2 = ESTransport(AMAZON_ES_DESCRIPTOR)
result = raw_transport2.send(
    'get', 
    "https://<Your endpoint here>/logs*/_search")
print(result)

