"""
models.py

Facebook module models.
"""
import requests
from flask import abort


class Facebook:
    def __init__(self, token):
        self.token = token
        pass

    def get(self, path, params=None):
        request_params = {
            'access_token': self.token,
            'format': 'json',
            'metho': 'get'
        }
        request_params.update(params)
        r = requests.get('https://graph.facebook.com/v2.5' + path, params=request_params)
        if r.status_code != 200:
            abort(r.status_code)
        return r.json()