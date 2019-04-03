'''
Copyright 2019, Amazon Web Services Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Python 3

Employs an es_line_buffer to hold log lines as they are added. Optionally
sends monitor information to an ES cluster. Set the flush_trigger to
control how many lines are buffered before each flush.
'''

from collections import namedtuple
import time

from es_line_buffer import ESLineBuffer
from transport import Transport

''' An ESDescriptor wraps the endpoint, index, and type for the buffer's 
    _bulk calls. Endpoint should be the full URL, including schema and 
    optionally including the port.'''
ESDescriptor = namedtuple('ESDescriptor', ['endpoint', 'es_index', 'es_type'])

class FlushingESBuffer():
    '''Wraps an ESLineBuffer object to provide _bulk flushing when the 
       flush_trigger is hit.'''

    def __init__(self, target_descriptor, signed=True,
                 flush_trigger=1):
        ''' target_descriptor must be an ESDescriptor'''
        self.transport = Transport(signed)
        self.target_descriptor = target_descriptor
        self.flush_trigger = flush_trigger
        self.buffer = ESLineBuffer(target_descriptor.es_index,
                                   target_descriptor.es_type)

    def add_log_line(self, log_line):
        '''Add a single log line to the internal buffer. If the flush trigger
           is hit, send the bulk request.'''
        self.buffer.add_log_line(log_line)
        if self.buffer.es_doc_count() >= self.flush_trigger:
            print("Flushing documents {}".format(time.time()))
            self.flush() # swallows the result. Do something with it?

    def flush(self):
        '''Flushes the line_buffer, sending all to the _bulk API'''
        if self.buffer.es_doc_count() > 0:
            try:
                url = "{}/_bulk/".format(self.target_descriptor.endpoint)
                result = self.transport.send("post", url, body=str(self.buffer))
                result = result._asdict()
                result['docs'] = self.buffer.es_doc_count()
                self.buffer.clear()
                return result
            except Exception as exc:
                message = "Exception sending request '{}'"
                print(message.format(str(exc)))
                raise exc
        return None
