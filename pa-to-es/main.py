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

This walks all of the combinations of metrics, dimensions, and aggregations.
METRICS - contains descriptions of the metric to be pulled and the dimensions
for that metric. See also the docs here:
https://opendistro.github.io/for-elasticsearch-docs/docs/pa/reference/. The
descriptions initially have None for the aggregations. These are added in the
loop below to send all the possible values 'min', 'max', 'avg', 'sum'.
'''

import argparse
import json

from datetime import datetime
import metric_descriptions
from pytz import timezone
import requests
from result_parser import ResultParser


class MetricGatherer():
    ''' Use this class to retrieve metrics from Open Distro's Performance
        Analyzer. Call get_all_metrics() to receive a list of ES docs. '''

    def __init__(self):
        pass

    def to_url_params(self, metric_description):
        '''Converts a metric description into the corresponding URL params'''
        return "metrics={}&dim={}&agg={}&nodes=all".format(
            metric_description.name, ",".join(metric_description.dimensions),
            metric_description.agg)

    def get_metric(self, metric_description):
        ''' Retrieves data for the metric represented by metric_description from 
            the Performance Analyzer API. Returns the full result from the 
            HTTP Requests library. '''
        BASE_URL = 'http://localhost:9600/_opendistro/_performanceanalyzer/metrics?'
        url = "{}{}".format(BASE_URL, self.to_url_params(metric_description))
        return requests.get(url)

    def get_all_metrics(self):
        ''' Loops through all the metric descriptions, sending one at a time,
            parsing the results, and returning a list of dicts, each one 
            representing one future Elasticsearch document. '''
        docs = []
        for metric in metric_descriptions.get_working_metric_descriptions():
            result = self.get_metric(metric)
            if result.status_code != 200:
                print("FAIL", metric, '\n', result.text)
            else:
                rp = ResultParser(metric, result.text)
                for doc in rp.records():
                    docs.append(doc)
        return docs


class MetricWriter():
    ''' Use this class to send documents in bulk to Elasticsearch'''

    def __init__(self, args):
        ''' Recieves the command-line args, which must include an index root,
            and an ES type. '''
        self.index_name = args.index_name 
        self.index_type = args.index_type

    def now_pst(self):
        '''Return the current time in PST timezone'''
        ''' TODO: This should use the timezone of the current host or UTC.'''
        now_utc = datetime.now(timezone('UTC'))
        return now_utc.astimezone(timezone('US/Pacific'))

    def put_doc_batches(self, docs):
        ''' Takes a list of Elasticsearch documents, interleaves the control
            lines and sends them via the _bulk API.'''
        batch = []
        for doc in docs:
            ''' It would be better to take the index name from the doc's
                timestamp. Otherwise weird stuff happens at midnight.'''
            index_name = "{}-{}".format(self.index_name,
                                        self.now_pst().strftime("%Y.%m.%d"))
            control_line = '{{"index" : {{ "_index" : "{}", "_type": "{}" }} }}'
            control_line = control_line.format(index_name, self.index_type)
            batch.append(control_line)
            batch.append(json.JSONEncoder().encode(doc))

        bulk = '\n'.join(batch) + '\n'
        print("Sending batch of {} characters".format(len(bulk)))
        result = requests.post('https://localhost:9200/_bulk', 
                               data=bulk,
                               headers={'Content-Type':'application/json'},
                               ### HACK ALERT !!! TODO TODO TODO ###
                               auth=('admin', 'admin'),
                               verify=False)
        print('Sent batch', result.status_code)

def get_args():
    ''' Parse command line arguments '''
    description = 'Send performance data from Open Distro for Elasticsearch to Elasticsearch'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-i', '--index-name', type=str, default='pa',
                        help='root string for the index name for performance indexes', 
                        action='store')
    parser.add_argument('-t', '--index-type', type=str, default='log',
                        help='root string for the index type for performance indexes', 
                        action='store')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    ''' This is the main function for the sample code provided.

            python3 main.py

        to run it. You can optionally set the ES index name (a timestamp is added
        to the --index-name, rolling over daily) and ES type via command-line.

        It's a simple-minded, not-very-efficient loop that pulls all metrics
        formats them, and pushes to Elasticsearch.

        On my Mac, this loop takes ~8 seconds. Ideally it would be < 5 seconds.
        Performance Analyzer aggregates across 5 second intervals, so this will
        miss some data points. The obvious fix for that is to get metrics in
        bulk, rather than one at a time.'''
    while 1:
        print('Gathering docs')
        docs = MetricGatherer().get_all_metrics()
        print('Sending docs: ', len(docs))
        MetricWriter(get_args()).put_doc_batches(docs)
