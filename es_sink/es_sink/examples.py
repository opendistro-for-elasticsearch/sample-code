import flushing_buffer
from descriptor import ESDescriptor, IndexDescriptor
import es_auth
from es_transport import ESTransport


################################################################################
# Example connecting to localhost with http auth
auth = es_auth.ESHttpAuth('admin', 'admin')
index_descriptor = IndexDescriptor(es_index='logs', es_v7=True, timestamped=True)
LOCALHOST_ESDESCRIPTOR = ESDescriptor("https://localhost:9200/", index_descriptor,
                                      auth=auth)

buffer = flushing_buffer.flushing_buffer_factory(LOCALHOST_ESDESCRIPTOR,
                                                 flush_trigger=1)

buffer.add_log_line('{"field1": "value1", "field2": "value2"}')

raw_transport = ESTransport(LOCALHOST_ESDESCRIPTOR)
result = raw_transport.send('get', "https://localhost:9200/logs*/_search")
print(result)


################################################################################
# Example connecting to Amazon Elasticsearch Service with signed requests

AMAZON_ES_ENDPOINT = "https://your endpoint here"
amzn_auth = es_auth.ESSigV4Auth()
amzn_index_descriptor = IndexDescriptor(es_index='logs', es_v7=True,
                                        timestamped=True)
AMAZON_ES_DESCRIPTOR = ESDescriptor(AMAZON_ES_ENDPOINT, amzn_index_descriptor,
                                    auth=amzn_auth)

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

