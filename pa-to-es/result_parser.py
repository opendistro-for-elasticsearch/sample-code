'''
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0

 result_parser provides a class that takes the results of calling the performance
 analyzer and putting together a document suitable for sending to Elasticsearch
 '''
import json

class ResultParser():
    ''' Construct with the text response from calling performance analyzer. Use
        the records() method to iterate over the response, retrieving a single
        Elasticsearch doc with each call. '''

    def __init__(self, metric, response_text, node_tracker):
        '''response_text is the body of the response to the GET request.'''
        self.response_json = json.loads(response_text)
        self.metric = metric
        self.node_tracker = node_tracker

    def _unpack_record(self, fields, record):
        ''' Match the field names with their values in the record. If there's no
            applicable value for the field (it's "null"), don't add the field to
            the doc. Returns a dict, which is the basis for the doc.'''
        ret = {'metric': self.metric.name}
        for field_name, value in zip(fields, record):
            if value is None or value == 'null':
                continue
            ret[field_name] = value
        return ret

    def records(self):
        ''' Iterates the response, yielding one dict at a time with a single
            metric and dimension

            A word on the API. PA returns a record for each combination
            of the requested dimensions. If a dimension doesn't bear on that
            particular metric, PA returns the string "null". To create the
            ES doc, you want to expose the combinations of dimensions that
            have values for that metric, skipping dimensions that have
            "null". The null dimensions are stripped out in _unpack_record. '''
        for node_name, values in self.response_json.items():
            node_ip = self.node_tracker.ip(node_name)
            timestamp = values['timestamp']
            data = values['data']
            if not data:
                break
            field_names = [x['name'] for x in data['fields']]
            records = data['records']
            for record in records:
                doc = self._unpack_record(field_names, record)
                if not doc:
                    continue
                doc['node_name'] = node_name
                doc['node_ip'] = node_ip
                doc['@timestamp'] = timestamp
                doc['agg'] = self.metric.agg
                yield doc
