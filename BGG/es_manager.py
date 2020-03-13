from es_sink import flushing_buffer
from es_sink.descriptor import ESDescriptor
from es_sink.es_transport import ESTransport

class ESManager():
    def __init__(self):
        # Todo - move these into parameters
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
        self.buffer.add_log_line(line)

    def remove_index(self, index_name):
        # Todo index name should come from __init__ params
        result = self.raw_transport.send('delete', 
                                         'https://localhost:9200/games')
        print("Deleted games index", result)

    def create_index(self, index_name, settings):
        # Todo index name should come from __init__ params
        result = self.raw_transport.send('put',
                                         'https://localhost:9200/games',
                                         body=settings)

    def flush(self):
        self.buffer.flush()
