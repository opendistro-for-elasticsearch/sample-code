'''
Copyright 2020, Amazon Web Services Inc.
This code is licensed under MIT license (see LICENSE.txt for details)

Python 3

ESTransport class
 Wrapper around the requests library that supports sending requests to
Elasticsearch.

 Use the signed initializer to control whether requests are signed with
sigV4 auth (via the requests_aws4auth library). When requests are signed
Transport gets credentials from the environment via Boto.
'''

import boto3
import requests
from requests_aws4auth import AWS4Auth

from es_sink.transport_result import TransportResult
from es_sink.transport_exceptions import BadHTTPMethod
from es_sink.transport_utils import wall_time, valid_request_body


def _get_requests_function(method):
    ''' Pull the right method from requests. '''
    try:
        func = getattr(requests, method)
        return func
    except AttributeError:
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


def _send_unsigned(method, url, body=None, http_auth=None):
    ''' Internal method to pass the request through. '''
    body = valid_request_body(body)
    func = _get_requests_function(method)
    if http_auth:
        (result, took_time) = \
            wall_time(func, url, data=body,
                      headers={"Content-Type":"application/json"},
                      auth=http_auth,
                      verify=False)
        return TransportResult(status=int(result.status_code),
                               result_text=result.text, took_s=took_time,
                               size=len(body))
    (result, took_time) = \
        wall_time(func, url, data=body,
                  headers={"Content-Type":"application/json"},
                  verify=False)
    return TransportResult(status=int(result.status_code),
                           result_text=result.text, took_s=took_time,
                           size=len(body))


class ESTransport():
    ''' Transport class, wrapping the requests library to add auth when needed
        and to provide a facade for Amazon ES domains and local Elasticsearch
        instances.'''

    def __init__(self, descriptor):
        '''A transport object to send requests to Elasticsearch. Since the class
           supports both Amazon ES domains and vanilla ES clusters, this needs
           to provide request signing as well as HTTP auth. The ESDescriptor
           specifies which of these to use. At present, there's no way to
           add http auth AND sign requests.
           TODO: implement lower-level request signing for signed HTTP auth

           descriptor.signed:       Set True to use SigV4 signing only
                                    Set False for HTTP Auth or no auth
           descriptor.http_auth:    User name, password tuple '''

        self._descriptor = descriptor

        if descriptor.is_signed() and descriptor.is_http_auth():
            raise BadAuth('You can\'t specify both HTTP auth and signed requests')

        if descriptor.is_signed() and not descriptor.region:
            raise ValueError('If you specify signed requests, you must also specify region')

    @property
    def is_signed(self):
        ''' Tracks whether to send signed requests '''
        return self._descriptor.is_signed()

    def send(self, method, url, service='es', body=''):
        '''Public method to dispatch between signed and unsigned.

           Specify the full URL, including endpoint.
           TODO: make the endpoint implicit, as determined by 
           descriptor.base_url(). This might be easier, but introduces
           complexity in using the class (how to know how much of the URL to
           specify)'''
        if self.is_signed:
            return _send_signed(method, url, service, self._descriptor.region,
                                body=body)
        return _send_unsigned(method, url, body=body,
                              http_auth=self._descriptor.http_auth)
