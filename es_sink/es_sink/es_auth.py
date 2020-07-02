'''
Copyright 2020, Amazon Web Services Inc.
This code is licensed under MIT license (see LICENSE.txt for details)

Python 3

Provides a class hierarchy to specify authentication method for the
ESDescriptor.

I'm not clear that the class hierarchy is buying me anything here. I
thought about a dict or namedtuple for these as well. The one thing
I get is in the transport layer, I can dispatch on the auth type. This
way is also more self-documenting.

'''


from abc import ABC, abstractmethod


class ESAuth(ABC):
    ''' Base class for the hierarchy. Nothing to do here.'''
    @abstractmethod
    def __init__(self):
        pass


class ESNoAuth(ESAuth):
    ''' Use to specify that no authentication will be added to the low-level
        transport.'''
    def __init__(self):
        super(ESNoAuth, self).__init__()


class ESSigV4Auth(ESAuth):
    ''' Use this to have the transport layer grab credentials via Boto. '''
    # Placeholder - eventually should support all of the different auth methods
    # of specifying access/secret and tokens.
    # Possibly this could do something like: boto3.Session().get_credentials()
    def __init__(self):
        super(ESSigV4Auth, self).__init__()


class ESHttpAuth(ESAuth):
    ''' Use with username/password for auth '''
    def __init__(self, user, password):
        super(ESHttpAuth, self).__init__()
        self._user = user
        self._password = password

    @property
    def user(self):
        return self._user

    @property
    def password(self):
        return self._password

    def as_tuple(self):
        return (self._user, self._password)
