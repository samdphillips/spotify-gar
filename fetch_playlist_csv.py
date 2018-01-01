
# python3

import csv
import logging
import requests
import sys

from requests.auth import AuthBase

# logging.basicConfig(level=logging.DEBUG)

URI_PATTERN = "https://api.spotify.com/v1/users/{user_id}/playlists/{playlist_id}/tracks"
FIELD_FILTER = "next,items(track(name,artists(name),album(name)))"


class SimpleBearerAuth(AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, request):
        request.headers['Authorization'] = 'Bearer {0}'.format(self.token)
        return request


class TrackFetcher:
    def __init__(self, user_id, playlist_id, token):
        self.endpoint = URI_PATTERN.format(playlist_id=playlist_id, user_id=user_id)
        self.http = requests.Session()
        self.http.auth=SimpleBearerAuth(token)

    def cleanse(self, item):
        t = item['track']
        return {
            'album': t['album']['name'],
            'name': t['name'],
            'artist': ', '.join([x['name'] for x in t['artists']])
        }

    def fetch(self):
        while True:
            params = { 'fields': FIELD_FILTER }
            response = self.http.get(self.endpoint, params=params)
            response.raise_for_status()
            response = response.json()
            for item in response['items']:
                yield item
            self.endpoint = response.get('next', None)
            params = {}
            if not self.endpoint:
                break

    def __iter__(self):
        for i in self.fetch():
            yield self.cleanse(i)


user_id, playlist_id, token = sys.argv[1:]
t = TrackFetcher(user_id, playlist_id, token)
# with open('playlist.csv', 'w') as outfile:
w = csv.DictWriter(sys.stdout, 'album artist name'.split())
w.writeheader()
w.writerows(t)
