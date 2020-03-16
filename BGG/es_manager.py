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


''' Provides the ESManager class. This class provides the interface to write the
boardgame documents to Elasticsearch. 

It uses the es_sink library to send the data and handle all auth. At the moment
the endpoint and other parameters are hard coded in the __init__ method via the
ESDescriptor object. See descriptor.py in the es_sink package for details on the
possible values for these parameters. 

It might be worth it to make those parameters available on the command line, but
hey, it's demo code!
'''


from es_sink import flushing_buffer
from es_sink.descriptor import ESDescriptor
from es_sink.es_transport import ESTransport


class ESManager():
    ''' Provides an interface to es_sink to connect and send data to 
        Elasticsearch. '''

    def __init__(self):
        ''' Hard-coded the descriptor. This instantiates a FlushingBuffer to
            enable ES transport. '''
        self.descriptor = ESDescriptor("https://localhost:9200/",
                                       es_v7=True,
                                       es_index='games',
                                       timestamped=False,
                                       signed=False,
                                       http_auth=('admin', 'admin'))
        self.buffer = flushing_buffer.flushing_buffer_factory(
            self.descriptor, flush_trigger=10000)
        self.raw_transport = ESTransport(self.descriptor)

    def add_document(self, line):
        ''' Add a document to the buffer. Can be a dict or string. '''
        self.buffer.add_log_line(line)

    def remove_index(self, index_name):
        ''' Supports removal of the games index to prepare for a clean upload.
            The index name is hard-coded here and in the descriptor. Probably
            not the best choice. '''
        result = self.raw_transport.send('delete', 
                                         'https://localhost:9200/games')
        print("Deleted games index", result)

    def create_index(self, index_name, settings):
        ''' Create an index to hold the stored games. The index name is hard-
            coded, which is not the best choice. If you change it here, be sure
            to change __init__ and remove_index to match. '''
        result = self.raw_transport.send('put',
                                         'https://localhost:9200/games',
                                         body=settings)

    def flush(self):
        ''' When the number of documents % flush_trigger is not 0, you need to
            do a final flush on the buffer. '''
        self.buffer.flush()
