# Some code provided by OnTheWind: https://github.com/OnTheWind/LegacyBot

import requests


class BrokkolyBotTwitch:
    def __init__(self, twitch_id, twitch_secret):
        self.twitch_id = twitch_id
        self.access_token = ""
        self.twitch_secret = twitch_secret
        self.base_url = 'https://api.twitch.tv'
        self.try_get_token()
        # self.get_user_info('ylokkorb')
        # print(self.access_token)
        # response=requests.get('https://api.twitch.tv/helix/users?id=ylokkorb')

    def get_user_info(self, username):
        response = requests.get(
            self.base_url + '/helix/users?login=' + username,
            headers={'Authorization': 'Bearer %s' % self.access_token, 'Client-Id': '%s' % self.twitch_id})

        print(response.text)
        # print(response.json()['data'][0])
        return response.json()['data'][0]

    def get_twitch_id(self, username):
        j = self.get_user_info(username)
        return j["id"]

    def try_get_token(self):
        response = requests.post(
            'https://id.twitch.tv/oauth2/token?&client_id=%s&client_secret=%s&grant_type=client_credentials' % (
                self.twitch_id, self.twitch_secret))
        j = response.json()
        if response.json()['access_token']:
            self.access_token = response.json()['access_token']


if __name__ == "__main__":
    print('getting')
    response = requests.get('http://localhost:44320/api/Twitch/StreamChange')
    response = requests.post('http://localhost:44320/api/Twitch/StreamChange', json={
        "data": [
            {
                "id": "0123456789",
                "user_id": "60294526",
                "user_name": "ylokkorb",
                "game_id": "21779",
                "community_ids": [],
                "type": "live",
                "title": "Best Stream Ever",
                "viewer_count": 417,
                "started_at": "2017-12-01T10:09:45Z",
                "language": "en",
                "thumbnail_url": "https://link/to/thumbnail.jpg"
            }
        ]})
    print('posted')
