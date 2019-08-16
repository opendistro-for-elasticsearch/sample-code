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

Transport class
 Wrapper around the requests library that supports sending requests to
Elasticsearch.

 Use the signed initializer to control whether requests are signed with
sigV4 auth (via the requests_aws4auth library). When requests are signed
Transport gets credentials from the environment via Boto. 
'''

import time

import boto3
import requests
from requests_aws4auth import AWS4Auth
from requests.auth import HTTPBasicAuth # this needs a way better solution

from transport_result import TransportResult
from transport_exceptions import TransportException, BadHTTPMethod


def valid_request_body(body):
    ''' Helper function to ensure request bodies terminate with a new line
        and to replace None with the empty string.'''
    if body and not body.endswith("\n"):
        body += "\n"
    elif not body:
        body = ""
    return body


def wall_time(func, *args, **kwargs):
    ''' Helper function to wrap the request and return wall time along with
        the result of the call. Not using clock() since the processing
        happens remotely.'''
    start = time.time()
    result = func(*args, **kwargs)
    end = time.time()
    return (result, end - start)


def _get_requests_function(method):
    ''' Pull the right method from requests. '''
    try:
        func = getattr(requests, method)
        return func
    except AttributeError as at_err:
        msg = "{} not a recognized HTTP method".format(method)
        raise BadHTTPMethod(msg)


def _send_signed(method, url, service='es', region='us-west-2', body=None):
    '''Internal method that uses sigV4 signing to send the request.'''
    credentials = boto3.Session().get_credentials()
    auth = AWS4Auth(credentials.access_key, credentials.secret_key, region,
                    service, session_token=credentials.token)
    func = _get_requests_function(method)
    (result, took_time) = \
        wall_time(func, url, auth=auth, data=valid_request_body(body),
                  headers={"Content-Type":"application/json"})
    return TransportResult(status=int(result.status_code),
                           result_text=result.text, took_s=took_time,
                           size=len(body))


def _send_unsigned(method, url, body=None):
    ''' Internal method to pass the request through. '''
    body = valid_request_body(body)
    func = _get_requests_function(method)
    (result, took_time) = \
        wall_time(func, url, data=body,
                  headers={"Content-Type":"application/json"},
                  ### HACK ALERT !!! TODO TODO TODO ###
                  #Remove this if you're using Amazon Managed ElasticSearch, and no authentication enabled.
                  #auth=('admin', 'admin'),
                  verify=False)
    print(result)
    return TransportResult(status=int(result.status_code),
                           result_text=result.text, took_s=took_time,
                           size=len(body))


class Transport(object):
    ''' Transport class, wrapping the requests library to add auth when needed
        and to provide a facade for Amazon ES domains and local Elasticsearch
        instances.'''

    def __init__(self, signed=True):
        ''' Set signed=True to use the sigV4 signing. False to send without.'''
        self._signed = signed

    @property
    def signed(self):
        ''' Tracks whether to send signed requests '''
        return self._signed

    def send(self, method, url, service='es', region='us-west-2', body=None):
        ''' Public method to dispatch between signed and unsigned. '''
        if self.signed:
            return _send_signed(method, url, service, region, body)
        else:
            return _send_unsigned(method, url, body)

