# Some code provided by OnTheWind: https://github.com/OnTheWind/LegacyBot

import requests


class BrokkolyBotTwitch:
    def __init__(self, twitch_id, twitch_secret):
        self.twitch_id = twitch_id
        self.access_token = ""
        self.twitch_secret = twitch_secret
        self.base_url = 'https://api.twitch.tv'
        self.try_get_token()
        # self.get_user_info('Ylokkorb')
        # response=requests.get('https://api.twitch.tv/helix/users?id=ylokkorb')

    def get_user_info(self, username):
        response = requests.get(
            self.base_url + '/helix/users?login=' + username,
            headers={'Authorization': 'Bearer %s' % self.access_token, 'Client-Id': '%s' % self.twitch_id})

        # print(response.text)
        # print(response.json()['data'][0])
        return response.json()['data'][0]

    def get_twitch_id(self, username):
        j = self.get_user_info(username)
        return j["id"]

    def try_get_token(self):
        response = requests.post(
            'https://id.twitch.tv/oauth2/token?&client_id=%s&client_secret=%s&grant_type=client_credentials' % (
                self.twitch_id, self.twitch_secret))
        if response.json()['access_token']:
            self.access_token = response.json()['access_token']

    def build_subscription(self, username):
        twitch_id = self.get_twitch_id(username)
        json_content = {'hub.callback': "brokkolybot.herokuapp.com" + '/api/Twitch/StreamChange?username=' + username,
                        'hub.mode': 'subscribe',
                        'hub.topic': 'https://api.twitch.tv/helix/streams?user_id=' + twitch_id,
                        'hub.lease_seconds': 86400,
                        'hub.secret': self.twitch_secret
                        }
