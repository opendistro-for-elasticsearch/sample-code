'''
Copyright 2019, Amazon Web Services Inc.
This code is licensed under MIT license (see LICENSE.txt for details)

Python 3

Provides a buffer object that holds log lines in Elasticsearch _bulk
format. As each line is added, the buffer stores the control line
as well as the log line.
'''

import abc
import json


class LineBuffer():
    ''' An abstract base class for buffering log lines'''

    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self._line_buffer = list()

    @abc.abstractmethod
    def add_line_dict(self, dic):
        '''Children should add the log line to their internal buffer'''

    @abc.abstractmethod
    def add_line_str(self, line):
        '''Children should add the log line to their internal buffer'''

    @abc.abstractmethod
    def es_docs(self):
        '''Children should override to return a multi-line string with only the
           ES documents, not the control lines.'''

    @staticmethod
    def _dict_to_string(dic):
        ''' Encode a dict as a string. Silently swallows errors '''
        try:
            line = json.JSONEncoder().encode(dic)
            return line
        except UnicodeDecodeError as exc:
            msg = "unicode problem {}, skipping line: {}"
            print(msg.format(str(exc), dic))
            return ''

    def add_log_line(self, log_line):
        '''Send all log lines to this function.'''
        if isinstance(log_line, dict):
            self.add_line_dict(log_line)
        elif isinstance(log_line, str):
            self.add_line_str(log_line)
        else:
            raise ValueError('{} is neither str nor dict'.format(log_line))

    def clear(self):
        '''Empty the buffer.'''
        self._line_buffer = list()

    def es_docs_bytes(self):
        '''Return the byte count for the log lines in the buffer'''
        return len(self.es_docs().encode("utf8"))

    def buffer_bytes(self):
        '''Return the total size of the objects in the buffer. This includes
           the size of the control lines.'''
        return len(str(self).encode("utf8"))

    def __str__(self):
        return "\n".join(self._line_buffer) + "\n"

    def __repr__(self):
        return str(self)


class SQSLineBuffer(LineBuffer):
    '''Implementation of LineBuffer to buffer data for SQS output. SQS doesn't
       use ES control lines, of course. The workers reading the queue need to
       add those lines.'''
    def __init__(self):
        super().__init__(self) # PyLint claims this is useless. Is it?

    def add_line_str(self, line):
        self._line_buffer.append(line)

    def add_line_dict(self, dic):
        line = LineBuffer._dict_to_string(dic)
        self._line_buffer.append(line)

    def es_docs(self):
        '''Return a flattened string with the log lines in the buffer.'''
        return "\n".join(self._line_buffer) + "\n"

    def es_doc_count(self):
        '''Return the count of log lines in the buffer.'''
        return len(self._line_buffer)


class ESLineBuffer(LineBuffer):
    '''Send lines to this class as either dicts or strs and it will buffer
       a control line along with the log line. Use str() to retrieve the
       post body to be used with a _bulk request.'''

    def __init__(self, es_descriptor):
        '''Initialize with the ES index name root as well as the ES type. These
           are embedded in the control line.'''
        super().__init__()
        self.es_descriptor = es_descriptor

    def add_line_str(self, line):
        '''Buffer a log line and an indexing command for that line'''
        control_line = self.es_descriptor.bulk_control_line()
        self._line_buffer.append(control_line)
        self._line_buffer.append(line)

    def add_line_dict(self, dic):
        '''Buffer a log line and an indexing command for that line'''
        line = LineBuffer._dict_to_string(dic)
        self.add_line_str(line)

    def es_docs(self):
        '''Return just the log lines in the buffer.'''
        return "\n".join(self._line_buffer[1::2]) + "\n"

    def es_doc_count(self):
        '''Return the count of log lines in the buffer.'''
        return len(self._line_buffer) / 2
