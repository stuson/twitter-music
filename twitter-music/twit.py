import twitter
import json
import os
from sys import argv

class Twitter:
    def __init__(self, credentials):
        self.api = twitter.Api(**credentials)
    
    @staticmethod
    def filter_retweets(timeline):
        return [status for status in timeline if not status.text.startswith('RT @')]
    
    @staticmethod
    def filter_replies(timeline):
        return [status for status in timeline if not status.text.startswith('@')]

    def get_tweets(self, screen_name, count=200, include_retweets=True, include_replies=True):
        timeline = self.api.GetUserTimeline(screen_name=screen_name, count=count)
        if not include_retweets or not include_replies:
            earliest = min(timeline, key=lambda x: x.id).id
            
            if not include_retweets:
                timeline = self.filter_retweets(timeline)
            
            if not include_replies:
                timeline = self.filter_replies(timeline)

            while len(timeline) < count:
                extra = self.api.GetUserTimeline(
                    screen_name=screen_name,
                    count=1 + count - len(timeline),
                    max_id=earliest
                )
                extra_earliest = min(extra, key=lambda x: x.id).id

                if not extra or extra_earliest == earliest:
                    break
                else:
                    earliest = extra_earliest
                    
                    if not include_retweets:
                        extra = self.filter_retweets(extra)
                    
                    if not include_replies:
                        extra = self.filter_replies(extra)

                    timeline += extra[1:]

        return timeline

def main():
    with open(
            os.path.join(
                os.path.dirname(__file__),
                'data/credentials.json'
            ),
            'r'
    ) as credentials_file:
        credentials = json.load(credentials_file)

    t = Twitter(credentials)

    tweets = t.get_tweets(
        argv[1],
        count=20,
        include_retweets='--include-retweets' in argv,
        include_replies='--include-replies' in argv
    )
    
    for i, tweet in enumerate(tweets):
        print(f'{i}: {tweet.created_at}')
        print(tweet.text)

if __name__ == "__main__":
    main()