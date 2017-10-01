"""
Просто получаем TOKEN.
"""
from urllib.parse import urlencode


AUTORIZE_URL = 'https://oauth.vk.com/authorize'
API_ID = 6195014
VERSION = 5.68

autorize = {
    'client_id': API_ID,
    'redirect_uri': 'https://oauth.vk.com/blank.html',
    'scope': 'friends,groups',
    'response_type': 'token',
    'v': VERSION
}

print('?'.join((AUTORIZE_URL,urlencode(autorize))))