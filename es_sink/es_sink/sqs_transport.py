'''
Copyright 2020, Amazon Web Services Inc.
This code is licensed under MIT license (see LICENSE.txt for details)

Python 3

PyLint complains about the Queue member of the boto3 SQS resource. If also
complains the SQSTransport class has too few methods. This disables both.'''
# pylint: disable=no-member,R0903


import boto3
from es_sink.transport_result import TransportResult
from es_sink.transport_utils import wall_time

class SQSTransport():
    ''' Transport class, wrapping the requests library to add auth when needed
        and to provide a facade for Amazon ES domains and local Elasticsearch
        instances.'''

    def __init__(self, target_descriptor):
        ''' Set signed=True to use the sigV4 signing. False to send without.'''
        self.target_descriptor = target_descriptor

    def send(self, body):
        '''Send a message to SQS. Returns a TransportResult'''
        sqs = boto3.resource('sqs', region_name=self.target_descriptor.region)
        queue = sqs.Queue(self.target_descriptor.sqs_url)
        (result, took_time) = wall_time(queue.send_message, MessageBody=body)
        metadata = result['ResponseMetadata']
        status = int(metadata['HTTPStatusCode'])
        size = int(metadata['HTTPHeaders']['content-length'])
        print(result)
        return TransportResult(status=status,
                               result_text='',
                               took_s=took_time,
                               size=size)
