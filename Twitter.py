# Imports
import json
from TwitterAPI import *
from requests_oauthlib import OAuth1, requests
from urlparse import parse_qs

class Twitter:
    """Twitter API abstraction class"""

    CONSUMER_KEY = ""
    CONSUMER_SECRET = ""
    ACCESS_TOKEN = ""
    ACCESS_TOKEN_SECRET = ""
    test = True

    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret, test):
        self.CONSUMER_KEY =  consumer_key
        self.CONSUMER_SECRET =  consumer_secret
        self.ACCESS_TOKEN =  access_token
        self.ACCESS_TOKEN_SECRET = access_token_secret
        self.test = test

    def auth(self):
        self.api = TwitterAPI(self.CONSUMER_KEY, self.CONSUMER_SECRET, self.ACCESS_TOKEN, self.ACCESS_TOKEN_SECRET)

    def timeline(self, screen_name):
        try:
            if self.test:
                response = TwitterPager(self.api, \
                                                "statuses/user_timeline", \
                                                {"screen_name": screen_name, \
                                                "count": 200, \
                                                "include_rts": True, \
                                                "trim_user": True})
            else:
                response = TwitterPager(self.api, \
                                                'tweets/search/%s/:%s' % ("30day", "test"), \
                                                {'query': 'from:' + screen_name})
            return response.get_iterator()
        except Exception as e:
            print e
        return response.get_iterator(wait=5)

    def tweet(self, id):
        return self.api.request('statuses/show/:%d' % id)

    def close(self):
        return None
