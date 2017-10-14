# TwitterListener.py
# by James Fulford
# Listens for tracking keywords through twitter. P


import tweepy
from credentials import credentials


consumer_key = credentials["twitter"]["consumer_key"]
consumer_secret = credentials["twitter"]["consumer_secret"]
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)

access_token = credentials["twitter"]["access_token"]
access_token_secret = credentials["twitter"]["access_token_secret"]
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)


def tweet(message):
    api.update_status(status=message)


class MyStreamListener(tweepy.StreamListener):
    def on_status(self, status):
        print u"{} ({}): {}\n".format(status.user.screen_name,
                                      status.user.followers_count,
                                      status.text)

    def on_error(self, status_code):
        if status_code == 420:
            # returning False in on_data disconnects the stream
            return False


myStream = tweepy.Stream(auth=api.auth, listener=MyStreamListener())

myStream.filter(track=['patriots'])
