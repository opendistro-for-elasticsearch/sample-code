'''
Copyright 2020, Amazon Web Services Inc.
This code is licensed under MIT license (see LICENSE.txt for details)

Python 3

Provides a buffer object that holds log lines in Elasticsearch _bulk
format. As each line is added, the buffer stores the control line
as well as the log line.
'''


from es_sink.transport_utils import now_pst


class SQSDescriptor():
    '''Description of an SQS queue. Enables generalization of sink targets'''
    def __init__(self, q_url, region):
        '''An SQS queue has a URL and a region'''
        self._sqs_url = q_url
        self._region = region

    @property
    def sqs_url(self):
        '''The target SQS URL'''
        return self. sqs_url

    @property
    def region(self):
        '''The region of the queue'''
        return self._region



class ESDescriptor():
    '''Description of an Elasticsearch endpoint.'''

    def __init__(self, endpoint, region=None, es_v7=False, es_index='',
                 es_type='', timestamped=True, signed=True, 
                 http_auth=None):
        '''Describes an ELasticsearch sink.

           This could be refactored to be a little bit better. As of now, it
           supports Amazon ES endpoints as well as vanilla ES endpoints. It also
           supports ES V6 and ES V7 endpoints. These could be mixins.

           endpoint:         The base url to send REST API calls
           region:           For Amazon ES domains, the AWS region. E.g.
                             us-west-2
           es_v7:            Use ES V7 APIs (no _type, mostly)
           es_index:         For API calls that use an index
           es_type:          For ES V6 clusters and calls that use a _type
           timestamped:      For ES API calls, mostly writes, append _YY.MM.DD
                             to the index name
           signed:           For Amazon ES domains, use SigV4 signing for
                             REST API calls. Uses Boto3 and requests-aws4auth to
                             pull credentials from the environment
           http_auth:        A tuple with (username, password) to use in sending
                             requests.'''
        self._endpoint = endpoint
        self._es_v7 = es_v7
        self._es_index = es_index
        self._es_type = es_type
        self._region = region
        self._signed = signed
        self._timestamped = timestamped
        self._http_auth = http_auth

    @property
    def http_auth(self):
        return self._http_auth
    

    @property
    def region(self):
        '''The region of the Amazon ES domain'''
        return self._region

    @property
    def signed(self):
        '''Should requests be signed with AWS SigV4 signing?'''
        return self._signed

    @property
    def timestamped(self):
        return self._timestamped
    

    def _index_name(self):
        ''' Return es_index-YY.MM.DD. Not timezone-aware '''
        if self._timestamped:
            return "{}-{}".format(self._es_index,
                                  now_pst().strftime("%Y.%m.%d"))
        return self._es_index

    def base_url(self):
        ''' Returns the endpoint. Slash-terminated.'''
        if self._endpoint.endswith('/'):
            return self._endpoint
        return '{}/'.format(self._endpoint)

    def base_url_with_index(self):
        '''Returns the endpoint/index, slash terminated. '''
        return '{}{}/'.format(self.base_url(), self._index_name())

    def base_url_6(self):
        ''' Returns the endpoint/index/type. Slash-terminated.
            Set timestamped=True to add the YY.MM.DD to the index
            name.'''
        return '{}{}/{}/'.format(self.base_url(), self._index_name(),
                                 self._es_type)

    def base_url_7(self):
        ''' Returns the endpoint/index/. Slash-terminated.
            Set timestamped=True to add the YY.MM.DD to the index
            name.'''
        return '{}{}/'.format(self.base_url(), self._index_name())

    def bulk_url(self):
        ''' d - an ESDescriptor. Returns the base url with _bulk.
            This assumes that you do not want index embedded.
            Set timestamped=True to add the YY.MM.DD to the index
            name.'''
        return '{}{}/_bulk'.format(self.base_url(), self._index_name())

    def search_url(self):
        ''' d - an ESDescriptor. Returns the base url with
            <es_index>/<es_type>/_search handles es v7 by removing the
            type. Set timestamped=True to add the YY.MM.DD to the index
            name.'''
        if self._es_v7:
            return '{}{}/_search'.format(self.base_url(),
                                         self._index_name())

        return '{}{}/{}/_search'.format(self.base_url(),
                                        self._index_name(),
                                        self._es_type)

    ACTION_LINE_6 = '{{"index" : {{ "_index" : "{}", "_type": "{}" }} }}'
    ACTION_LINE_7 = '{{"index" : {{ "_index" : "{}" }} }}'
    def bulk_control_line(self):
        ''' Strictly, this shouldn't go in this class. It's not really
            part of a description. OTOH, all the info is here and it will
            save lots of duplicated code.
            Returns the "control" line for a _bulk request. '''
        if self._es_v7:
            return self.ACTION_LINE_7.format(self._index_name())

        return self.ACTION_LINE_6.format(self._index_name(),
                                         self._es_type)
