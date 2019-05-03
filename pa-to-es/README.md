# Performance analyzer output to Elasticsearch

This library provides a main.py script that collects all of the metrics
surfaced by Performance Analyzer, across their dimensions and aggregations. It 
pushes those metrics to Elasticsearch for visualization with Kibana.

This initial version works with localhost only, presumably targeted at Open
Distro for Elasticsearch, running locally in containers.

## Requirements

The code requires Python 3
Libraries:
HTTP Requests
pytz

## Basic Usage

python3 main.py

NOTE: before running, apply the template in template.json to your cluster. If
you don't set the template, Elasticsearch will interpret the timestamp as a
long integer.

## Code of Conduct

This project has adopted an [Open Source Code of
Conduct](https://opendistro.github.io/for-elasticsearch/codeofconduct.html).


## Security issue notifications

If you discover a potential security issue in this project we ask that you
notify AWS/Amazon Security via our [vulnerability reporting
page](http://aws.amazon.com/security/vulnerability-reporting/). Please do
**not** create a public GitHub issue.


## Licensing

See the [LICENSE](./LICENSE) file for our project's licensing. We will ask you
to confirm the licensing of your contribution.


## Copyright

Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
