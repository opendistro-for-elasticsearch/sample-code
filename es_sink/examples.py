# MIT License
#
# Copyright (c) 2020 Amazon Web Services
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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
    "https://search-test-es-sink-nrobz6a4gwulmlh6kh6kdzer6u.us-west-2.es.amazonaws.com/logs*/_search")
print(result)

