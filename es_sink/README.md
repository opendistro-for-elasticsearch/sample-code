# es_sink Package

This package provides a set of modules for sending bulk requests to Elasticsearch. It can deliver _bulk requests to Elasticsearch versions < 7x and > 7x. It can deliver to any Elasticsearch cluster - open source, Open Distro for Elasticsearch, and Amazon Elasticsearch Service. It handles authentication in a number of different modalities.

## Examples

```
################################################################################
# Example connecting to localhost with http auth
LOCALHOST_ESDESCRIPTOR = ESDescriptor("https://localhost:9200/", es_v7=True, 
                                      es_index='logs', timestamped=True, 
                                      signed=False, http_auth=('admin', 'admin'))

buffer = flushing_buffer.flushing_buffer_factory(LOCALHOST_ESDESCRIPTOR,
                                                 flush_trigger=1)

buffer.add_log_line('{"field1": "value1", "field2": "value2"}')
                                                                     # For raw transport
raw_transport = ESTransport(LOCALHOST_ESDESCRIPTOR)
result = raw_transport.send('get', "https://localhost:9200/logs*/_search")


################################################################################
# Example connecting to Amazon Elasticsearch Service with signed requests

AMAZON_ES_ENDPOINT = "https://your endpoint here"
AMAZON_ES_DESCRIPTOR = ESDescriptor(AMAZON_ES_ENDPOINT, es_v7=True,
                                    es_index='logs', signed=True,
                                    region='us-west-2', timestamped=True)

buffer2 = flushing_buffer.flushing_buffer_factory(AMAZON_ES_DESCRIPTOR,
                                                 flush_trigger=1)

buffer2.add_log_line('{"field1": "value1", "field2": "value2"}')

# Raw transport for Amazon ES
raw_transport2 = ESTransport(AMAZON_ES_DESCRIPTOR)
result = raw_transport2.send(
    'get', 
    "https://search-test-es-sink-nrobz6a4gwulmlh6kh6kdzer6u.us-west-2.es.amazonaws.com/logs*/_search")
print(result)
                                                                                      
```

# Usage

Create an ESDescriptor for your domain. The ESDescriptor contains the following parameters:

- endpoint - The base url to send REST API calls
- region - For Amazon ES domains, the AWS region. E.g. us-west-2
- es_v7 - Use ES V7 APIs (no _type, mostly)
- es_index - For API calls that use an index
- es_type - For ES V6 clusters and calls that use a _type
- timestamped - For ES API calls, mostly writes, append _YY.MM.DD to the index name
- signed - For Amazon ES domains, use SigV4 signing for REST API calls. Uses Boto3 and requests-aws4auth to pull credentials from the environment
- http_auth - A tuple with (username, password) to use in sending

Pass the ESDescriptor to flushing_buffer_factory to create a buffer for your data. 

## FlushingBuffer

FlushingBuffer holds log lines until it reaches the flush_trigger, when it sends the full buffer to ES. Currently, there is no error checking or retries.

Use the add_log_line method of the FlushingBuffer to add single lines. You can pass in a string or a dict. If you send a dict, FlushingBuffer converts it to a string before sending.

## Transport

Underlying the communication is the ESTransport class. Use the send method directly to send REST requests to ES. 

## Elasticsearch and SQS

The es_sink package also includes classes that support sending log lines to Amazon Simple Queue Service (SQS). When sending to SQS, the buffer is queued as a multi-line string. 

Queueing in SQS supports a pattern of loading log lines into SQS and then employing the es_sink package in the worker nodes to deliver to Elasticsearch.

# Deployment

This package is not currently uploaded to PyPi. To install, download the package from GitHub. Assuming your folder structure looks like this

```
es_sink
\- setup.py
\- ...
\- es_sink
   \- __init__.py
   \- descriptor.py
   \- ...
```

Use ```pip install <full path to es_sink root>```

