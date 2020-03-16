'''
Copyright 2020, Amazon Web Services Inc.
This code is licensed under MIT license (see LICENSE.txt for details)

Python 3

Provides a buffer object that holds log lines in Elasticsearch _bulk
format. As each line is added, the buffer stores the control line
as well as the log line.

Employs an line_buffer to hold log lines as they are added. Optionally
sends monitor information to an ES cluster. Set the flush_trigger to
control how many lines are buffered before each flush.
'''

import time

from es_sink.descriptor import ESDescriptor, SQSDescriptor
from es_sink.line_buffer import ESLineBuffer, SQSLineBuffer
from es_sink.es_transport import ESTransport
from es_sink.sqs_transport import SQSTransport
from es_sink.transport_exceptions import BadSink

class FlushingESBuffer():
    '''Wraps an ESLineBuffer object to provide _bulk flushing when the
       flush_trigger is hit.'''

    def __init__(self, descriptor, flush_trigger=1):
        ''' target_descriptor must be an ESDescriptor'''
        self.transport = ESTransport(descriptor)
        self.target_descriptor = descriptor
        self.flush_trigger = flush_trigger
        self.buffer = ESLineBuffer(descriptor)

    def add_log_line(self, log_line):
        '''Add a single log line to the internal buffer. If the flush trigger
           is hit, send the bulk request.'''
        self.buffer.add_log_line(log_line)
        if self.buffer.es_doc_count() >= self.flush_trigger:
            self.flush() # swallows the result. Do something with it?

    def flush(self):
        '''Flushes the line_buffer, sending all to the _bulk API'''
        if self.buffer.es_doc_count() > 0:
            try:
                url = self.target_descriptor.bulk_url()
                print("Flushing {} documents {} to {}".format(
                    self.buffer.es_doc_count(),
                    time.time(),
                    url))
                result = self.transport.send('post', url, body=str(self.buffer))
                result = result._asdict()
                result['docs'] = self.buffer.es_doc_count()
                self.buffer.clear()
                return result
            except Exception as exc:
                message = "Exception sending request '{}'"
                print(message.format(str(exc)))
                raise exc
        return None


class FlushingSQSBuffer():
    '''Use to send ES _bulk data to SQS in batches.'''

    def __init__(self, descriptor, flush_trigger=1):
        self.target_descriptor = descriptor
        self.flush_trigger = flush_trigger
        self.transport = SQSTransport(descriptor)
        self.buffer = SQSLineBuffer()

    def add_log_line(self, line):
        '''Add a single log line to the internal buffer. If the flush trigger
           is hit, send the bulk request.'''
        self.buffer.add_log_line(line)
        if self.buffer.es_doc_count() >= self.flush_trigger:
            self.flush() # swallows the result. Do something with it?

    def flush(self):
        '''Flushes the line_buffer, sending all to the _bulk API'''
        print("Flushing {} documents {}".format(self.buffer.es_doc_count(),
                                                time.time()))
        if self.buffer.es_doc_count() > 0:
            result = self.transport.send(str(self.buffer))
            result = result._asdict()
            result['docs'] = self.buffer.es_doc_count()
            self.buffer.clear()
            print(result)
            return result
        return None


def flushing_buffer_factory(descriptor, flush_trigger=1):
    '''Call with a descriptor to receive a buffer object.'''
    if isinstance(descriptor, ESDescriptor):
        return FlushingESBuffer(descriptor, flush_trigger)

    if isinstance(descriptor, SQSDescriptor):
        return FlushingSQSBuffer(descriptor, flush_trigger)

    raise BadSink()
