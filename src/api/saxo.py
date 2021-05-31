import json
import os
from datetime import datetime

import random
import requests
import threading

API_URL = "https://gateway.saxobank.com/sim/openapi"
ME_URI = "port/v1/users/me"
REDIR_URI = "http://gttkeith.github.io/python-saxo/authcode"
ACCOUNT_KEY = 'ClientKey'


class Session:
    @staticmethod
    def new_state(stringLength=16):
        chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890"
        return ''.join(random.choice(chars) for i in range(stringLength))

    @staticmethod
    def process_uri(uri):
        if isinstance(uri, list):
            l = ['/' + s for s in uri]
            uri = ''.join(l)
        if not uri[0] == '/':
            uri = '/' + uri
        return uri

    def process_params(self, params):
        if 'AccountKey' not in params.keys():
            params['AccountKey'] = self.account_key
        return params

    def parse_json(self, token_json):
        self.token = token_json.get('access_token')
        self.expires_in = int(token_json.get('expires_in'))
        self.refresh = token_json.get('refresh_token')

    def periodic_token_refresh(self):
        self.expires_in -= 1
        if self.expires_in < 60:
            token_json = requests.post(self.token_endpoint,
                                       params={'grant_type': 'refresh_token', 'refresh_token': self.refresh,
                                               'redirect_uri': REDIR_URI, 'client_id': self.app_key,
                                               'client_secret': self.secret}).json()
            self.parse_json(token_json)

    def stream(self, uri, **params):
        return requests.get(API_URL + Session.process_uri(uri),
                            headers={'Authorization': 'Bearer ' + self.token, 'contextId': self.state},
                            params=self.process_params(params), stream=True)

    def get(self, uri, **params):
        return TypeManager.ensure_type_robustness(
            requests.get(API_URL + Session.process_uri(uri), headers={'Authorization': 'Bearer ' + self.token},
                         params=self.process_params(params)).json())

    def post(self, uri, post=None, **params):
        if post is None:
            post = {}

        return requests.post(API_URL + Session.process_uri(uri),
                             headers={'Authorization': 'Bearer ' + self.token, "Content-Type": "application/json"},
                             params=self.process_params(params), json=self.process_params(post)).json()

    def put(self, uri, **params):
        return requests.put(API_URL + Session.process_uri(uri), headers={'Authorization': 'Bearer ' + self.token},
                            params=self.process_params(params)).json()

    def delete(self, uri, **params):
        return requests.delete(API_URL + Session.process_uri(uri), headers={'Authorization': 'Bearer ' + self.token},
                               params=self.process_params(params)).json()

    def get_token(self, force_remove=False):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        auth_file_name = 'session'
        auth_file_path = os.path.join(current_dir, '../../', auth_file_name)

        if force_remove:
            os.remove(auth_file_path)

        try:
            auth_file = open(auth_file_path)
        except IOError:
            auth_file = open(auth_file_path, 'w+')

        auth_file_data = auth_file.read()

        if not auth_file_data:
            r = requests.get(self.auth_endpoint,
                             params={'response_type': 'code', 'client_id': self.app_key, 'state': self.state,
                                     'redirect_uri': REDIR_URI})
            print("Log in and obtain authcode: " + r.url)
            authcode = input("Paste authcode: ")
            token_json = requests.post(self.token_endpoint,
                                       params={'grant_type': 'authorization_code', 'code': authcode,
                                               'redirect_uri': REDIR_URI, 'client_id': self.app_key,
                                               'client_secret': self.secret}).json()
            auth_file.write(json.dumps(token_json))
        else:
            token_json = json.loads(auth_file_data)

        self.parse_json(token_json)

    def __init__(self, app_key, auth_endpoint, token_endpoint, secret):
        self.state = Session.new_state()
        self.app_key = app_key
        self.auth_endpoint = auth_endpoint
        self.token_endpoint = token_endpoint
        self.secret = secret

        self.get_token()
        me = requests.get(API_URL + '/' + ME_URI, headers={'Authorization': 'Bearer ' + self.token})
        if me.status_code == 401:
            self.get_token(force_remove=True)
            me = requests.get(API_URL + '/' + ME_URI, headers={'Authorization': 'Bearer ' + self.token})

        self.account_key = me.json()[ACCOUNT_KEY]

        threading.Timer(1, self.periodic_token_refresh).start()


class TypeManager:
    @staticmethod
    def ensure_type_robustness(data):
        if isinstance(data, dict):
            res = {}
            for k, v in data.items():
                res[k] = TypeManager.ensure_type_robustness(v)
            return res
        elif isinstance(data, list):
            return [TypeManager.ensure_type_robustness(v) for v in data]
        else:
            try:
                return UtcDateTime.from_string(data)
            except:
                return data


class UtcDateTime(datetime):
    @staticmethod
    def from_string(inp):
        return UtcDateTime.strptime(inp, '%Y-%m-%dT%H:%M:%S.%fZ')

    def __str__(self):
        return self.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    def to_string(self):
        return self.__str__()
