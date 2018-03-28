# pylint:disable=C0413, C0103
"""Get tweets."""
import os
import sys
sys.path.append(os.getcwd())
from datetime import datetime
import time
from dateutil.relativedelta import relativedelta
import yaml
import twitter
import pandas as pd
import numpy as np
from src.data.locations import CITIES, GEOCODES

RATE_LIMIT = 180
# RATE_LIMIT = 10

# delay 15 minutes after each RATE_LIMIT
DELAY = 900

COLUMNS = [
    'id', 'user', 'created_at', 'in_reply_to_screen_name',
    'retweet_count', 'retweeted_status', 'source',
    'text'
]

DROP_COLUMNS = ['in_reply_to_screen_name', 'retweeted_status']

DATES = [
    (datetime.today() - relativedelta(days=x-1)).strftime('%Y-%m-%d')
    for x in range(7)
]



def main():
    """Run on CLI."""
    for date in DATES:
        print(
            datetime.now().strftime('%Y-%m-%d %H:%M:%S -'),
            'Starting queries for', date
        )
        file_name =\
            './data/tweets_' + datetime.now().strftime('%Y%m%d%H%M') + '.csv'
        save_tweets('until:'+date, file_name)
        time.sleep(DELAY)

def asdict(x):
    """Enable function mapping."""
    return x.AsDict()

def save_tweets(term, file_name):
    """Query recent tweets from each city and save to csv."""
    with open('_access.yml', 'r') as f:
        twitter_access = yaml.load(f)['TWITTER']
        twitter_api = twitter.Api(
            consumer_key=twitter_access['API_KEY'],
            consumer_secret=twitter_access['API_SECRET'],
            access_token_key=twitter_access['ACCESS_TOKEN'],
            access_token_secret=twitter_access['ACCESS_TOKEN_SECRET'],
            application_only_auth=False
        )

    print(twitter_api.VerifyCredentials())
    print(
        datetime.now().strftime('%Y-%m-%d %H:%M:%S -'),
        'API access successful.'
    )

    df_all = pd.DataFrame()
    for ind in range(RATE_LIMIT):
        if np.mod(ind, 10) == 0:
            print(
                datetime.now().strftime('%Y-%m-%d %H:%M:%S -'),
                '...processing query', '%04d' % ind, '...')
        if ind == 0:
            _tweets = twitter_api.GetSearch(
                term=term,
                geocode=GEOCODES[np.mod(ind, len(GEOCODES))],
                result_type='recent',
                count=100
            )
            _after = _tweets[-1].id
        else:
            _tweets = twitter_api.GetSearch(
                term=term,
                geocode=GEOCODES[np.mod(ind, len(GEOCODES))],
                result_type='recent',
                max_id=(_after - 1),
                count=100
            )
            _after = _tweets[-1].id
        _dat = pd.DataFrame(list(map(asdict, _tweets)))
        _dat = _dat[COLUMNS]
        _dat['is_reply'] = _dat['in_reply_to_screen_name'].isnull() * (-1) + 1
        _dat['is_retweet'] = _dat['retweeted_status'].isnull() * (-1) + 1
        _dat['user'] = _dat['user'].apply(lambda x: x['id_str'])
        _dat['retweet_count'].fillna(0, inplace=True)
        _dat['city'] = CITIES[np.mod(ind, 5)]
        _dat.drop(DROP_COLUMNS, axis=1, inplace=True)
        df_all = df_all.append(_dat)

    df_all.drop_duplicates('id', inplace=True)

    # remove new lines from text
    df_all['text'].replace({r'[\r\n]+': r'\s'}, regex=True, inplace=True)
    df_all.to_csv(file_name, index=False)
    print(
        datetime.now().strftime('%Y-%m-%d %H:%M:%S -'),
        'Complete.')
    print(
        datetime.now().strftime('%Y-%m-%d %H:%M:%S -'),
        'Processed', df_all.shape[0], 'rows of data.')
    twitter_api.ClearCredentials()

if __name__ == '__main__':
    main()
