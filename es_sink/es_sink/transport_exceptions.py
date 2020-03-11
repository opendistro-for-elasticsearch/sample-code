'''
Copyright 2020, Amazon Web Services Inc.
This code is licensed under MIT license (see LICENSE.txt for details)

Python 3
'''
class TransportException(Exception):
    '''Raised by the transport layer for most issues.'''


class BadHTTPMethod(Exception):
    '''Raised for methods missing from the requests library.'''


class BadSink(Exception):
    '''Raised when the target descriptor for transport is not ESDescriptor or
       SQSDescriptor.'''


class BadAuth(Exception):
    '''Raised if the transport client gets both SigV4 signing and HTTP Auth'''