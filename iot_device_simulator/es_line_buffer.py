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

Provides a buffer object that holds log lines in Elasticsearch _bulk
format. As each line is added, the buffer gets the control line
as well as the log line.
'''

import json
import timeutil

class ESLineBuffer():
    '''Send lines to this class as either dicts or strs and it will buffer
       a control line along with the log line. Use str() to retrieve the
       post body to be used with a _bulk request.'''

    def __init__(self, es_index_pattern, es_type):
        '''Initialize with the ES index name root as well as the ES type. These
           are embedded in the control line.'''
        self.es_index_pattern = es_index_pattern
        self.es_type = es_type
        self.line_buffer = list()

    def add_line_str(self, log_line):
        '''Buffer a log line and an indexing command for that line'''
        index_name = "{}-{}".format(self.es_index_pattern,
                                    timeutil.now_pst().strftime("%Y.%m.%d"))

        control_line = '{{"index" : {{ "_index" : "{}", "_type": "{}" }} }}'
        control_line = control_line.format(index_name, self.es_type)
        self.line_buffer.append(control_line)
        self.line_buffer.append(log_line)

    def add_line_dict(self, log_line):
        '''Buffer a log line and an indexing command for that line'''
        try:
            json_encoded_line = json.JSONEncoder().encode(log_line)
        except UnicodeDecodeError as exc:
            print("unicode problem {}, skipping line: {}".format(str(exc), 
                                                                 log_line))
            return
        index_name = "{}-{}".format(self.es_index_pattern,
                                    timeutil.now_pst().strftime("%Y.%m.%d"))

        control_line = '{{"index" : {{ "_index" : "{}", "_type": "{}" }} }}'
        control_line = control_line.format(index_name, self.es_type)

        self.line_buffer.append(control_line)
        self.line_buffer.append(json_encoded_line)

    def add_log_line(self, log_line):
        '''Send all log lines to this function.'''
        if isinstance(log_line, dict):
            self.add_line_dict(log_line)
        elif isinstance(log_line, str):
            self.add_line_str(log_line)
        else:
            raise ValueError('{} is neither str nor dict'.format(log_line))

    def es_docs(self):
        '''Return just the log lines in the buffer.'''
        return "\n".join(self.line_buffer[1::2]) + "\n"

    def es_doc_count(self):
        '''Return the count of log lines in the buffer.'''
        return len(self.line_buffer) / 2

    def es_docs_bytes(self):
        '''Return the byte count for the log lines in the buffer'''
        return len(self.es_docs().encode("utf8"))

    def clear(self):
        '''Empty the buffer.'''
        self.line_buffer = list()

    def buffer_bytes(self):
        '''Return the total size of the objects in the buffer. This includes
           the size of the control lines.'''
        return len(str(self).encode("utf8"))

    def __str__(self):
        return "\n".join(self.line_buffer) + "\n"

    def __repr__(self):
        return str(self)
