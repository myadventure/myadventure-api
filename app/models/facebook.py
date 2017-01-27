"""
facebook.py

Facebook models.
"""

import requests
from flask import abort


class Facebook(object):
    """A platform user.

    """
    def __init__(self, token):
        self.token = token

    def get(self, path, params=None):
        """Get request to Facebook."""
        request_params = {
            'access_token': self.token,
            'format': 'json',
            'metho': 'get'
        }
        request_params.update(params)
        res = requests.get('https://graph.facebook.com/v2.5' + path, params=request_params)
        if res.status_code != 200:
            abort(res.status_code)
        return res.json()
