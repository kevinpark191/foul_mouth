"""Test script WIP."""
from datetime import datetime
import yaml
import twitter
import pandas as pd
import numpy as np
from locations import CITIES, GEOCODES
# from src.data.locations import CITIES, GEOCODES

RATE_LIMIT = 180

COLUMNS = [
    'id', 'user', 'created_at', 'in_reply_to_screen_name',
    'retweet_count', 'retweeted_status', 'source',
    'text'
]

DROP_COLUMNS = ['in_reply_to_screen_name', 'retweeted_status']

FILE_NAME = './data/tweets_' + datetime.now().strftime('%Y%m%d%H%M') + '.csv'

def main():
    """Run on CLI."""
    with open('_access.yml', 'r') as f:
        twitter_access = yaml.load(f)['TWITTER']
        twitter_api = twitter.Api(
            consumer_key=twitter_access['API_KEY'],
            consumer_secret=twitter_access['API_SECRET'],
            access_token_key=twitter_access['ACCESS_TOKEN'],
            access_token_secret=twitter_access['ACCESS_TOKEN_SECRET'],
            application_only_auth=False
        )

    locations = []
    tweets = []

    print(twitter_api.VerifyCredentials())
    print(
        datetime.now().strftime('%Y-%m-%d %H:%M:%S -'),
        'API access successful.')

    for ind in range(RATE_LIMIT):
        if np.mod(ind, 10) == 0:
            print(
                datetime.now().strftime('%Y-%m-%d %H:%M:%S -'),
                '...processing query', '%04d' % ind, '...')
        locations.append(CITIES[np.mod(ind, 5)])
        tweets.append(twitter_api.GetSearch(
            geocode=GEOCODES[np.mod(ind, len(GEOCODES))],
            result_type='recent',
            count=100
        ))

    def asdict(x):
        """Enable function mapping."""
        return x.AsDict()

    print(
        datetime.now().strftime('%Y-%m-%d %H:%M:%S -'),
        'Creating a dataframe...')
    df_all = pd.DataFrame()

    for (loc, twt) in zip(locations, tweets):
        dat = pd.DataFrame(list(map(asdict, twt)))
        dat = dat[COLUMNS]
        dat['is_reply'] = dat['in_reply_to_screen_name'].isnull() * (-1) + 1
        # dat['is_truncated'] = dat['truncated'].isnull() * (-1) + 1
        dat['is_retweet'] = dat['retweeted_status'].isnull() * (-1) + 1
        dat['city'] = loc
        dat['user'] = dat['user'].apply(lambda x: x['id_str'])
        dat['retweet_count'].fillna(0, inplace=True)
        dat.drop(DROP_COLUMNS, axis=1, inplace=True)
        df_all = df_all.append(dat)

    df_all.drop_duplicates('id', inplace=True)

    # remove new lines from text
    df_all['text'].replace({r'\n': r'\s'}, regex=True)
    df_all.to_csv(FILE_NAME, index=False)
    print(
        datetime.now().strftime('%Y-%m-%d %H:%M:%S -'),
        'Complete.')
    print(
        datetime.now().strftime('%Y-%m-%d %H:%M:%S -'),
        'Processed', df_all.shape[0], 'rows of data.')
    twitter_api.ClearCredentials()

if __name__ == '__main__':
    main()
