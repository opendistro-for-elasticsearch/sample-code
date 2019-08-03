'''
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0

This walks all of the combinations of metrics, dimensions, and aggregations.
METRICS - contains descriptions of the metric to be pulled and the dimensions
for that metric. See also the docs here:
https://opendistro.github.io/for-elasticsearch-docs/docs/pa/reference/.
'''
import json

import requests

class NodeTracker():
    ''' Discovers nodes in the cluster, and holds a map from node name to
        ip address. Construct the object, then use ip() to retrieve the 
        address from the node name.'''

    def __init__(self):
        ''' Constructs a local dict, and fills it.'''
        self._nodes_map = dict()
        self._retrieve_node_ids_and_ips()

    def _retrieve_node_ids_and_ips(self):
        ''' Use _cat/nodes to pull the name and IP for all of the nodes in
            the cluster. '''
        response = requests.get('https://localhost:9200/_nodes',
            ### HACK ALERT !!! TODO TODO TODO!!! Add real auth ###
            auth=('admin', 'admin'),
            verify=False)
        if int(response.status_code) >= 300:
            raise Exception('Bad response code trying to get node names and ips') 
        json_response = json.loads(response.text)
        if 'nodes' not in json_response:
            raise Exception('Bad response - no nodes') 
        for node_id, values in json_response['nodes'].items():
            self._nodes_map[node_id] = values['ip']

    def ip(self, node_name):
        if node_name in self._nodes_map:
            return self._nodes_map[node_name]
        raise ValueError('{} is not a recognized node name'.format(node_name))

    def print_table(self):
        for name, ip in self._nodes_map.items():
            print(' {}    {}'.format(name, ip))
