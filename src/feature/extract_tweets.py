# pylint:disable=C0413
"""Extract features from tweets."""
import os
import sys
sys.path.append(os.getcwd())
from datetime import datetime
import glob
import pytz
import pandas as pd
from src.utils import TIMEZONES

READ_FILE_NAME = './data/tweets_'
WRITE_FILE_NAME = './data/feat_tweets_' \
    + datetime.now().strftime('%Y%m%d%H%M') + '.csv'

def main():
    """Run from CLI."""
    files = glob.glob(READ_FILE_NAME+'*')
    files.sort()
    tweets = pd.read_csv(files[-1])

    # drop rows with missing values and duplicates
    tweets.dropna(axis=0, how='any', inplace=True)
    tweets.drop_duplicates('id', inplace=True)

    # make user id a string
    tweets['user'] = tweets['user'].map(lambda x: 'UID%019d' % x)

    # save utc and local times
    tweets['utc_time'] = tweets['created_at'].map(
        lambda x: datetime.strptime(
            x, '%a %b %d %H:%M:%S +0000 %Y'
        ).replace(tzinfo=pytz.utc)
    )
    tweets['local_time'] = tweets.apply(
        lambda row: TIMEZONES[row['city']].normalize(row['utc_time']),
        axis=1
    )
    tweets['local_hour'] = tweets['local_time'].map(lambda x: x.hour)
    tweets['weekday'] = tweets['local_time'].map(lambda x: x.weekday())
    tweets['month'] = tweets['local_time'].map(lambda x: x.month)

    # extract source
    tweets['source'] = tweets['source'].map(
        lambda x: x.split('>')[1].split('<')[0].strip()
    )
    btm_95pct_sources = tweets['source'].value_counts()[
        tweets['source'].value_counts().cumsum()
        > tweets['source'].value_counts().sum() * 0.95
    ]
    for other in btm_95pct_sources.index:
        tweets['source'].replace({other: 'Other'}, inplace=True)

    # remove new lines from tweets
    tweets['text'].replace({r'\n': r'\s'}, regex=True, inplace=True)

    # TODO: tokenize text

    tweets.drop(['created_at', 'id'], axis=1, inplace=True)

    tweets.to_csv(WRITE_FILE_NAME)

if __name__ == '__main__':
    main()
