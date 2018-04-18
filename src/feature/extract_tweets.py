# pylint:disable=C0413
"""Extract features from tweets."""
import os
import sys
sys.path.append(os.getcwd())
from datetime import datetime
import glob
import pytz
import pandas as pd
from nltk.tokenize import TweetTokenizer
from src.utils import TIMEZONES, is_word
from src.utils.badwords import BadWords

READ_FILE_NAME = './data/tweets_'
WRITE_FILE_NAME = './data/feat_tweets_' \
    + datetime.now().strftime('%Y%m%d%H%M') + '.csv'

# use nltk TweetTokenizer to
# 1) tokenize urls and
# 2) exclude user handles
TWEET_TOKENIZER = TweetTokenizer(
    preserve_case=False,
    reduce_len=True,
    strip_handles=True
)

# bad word identifier
BAD_WORDS = BadWords()

def extract_features(tweets):
    """Extract features."""
    # drop rows with missing values and duplicates
    tweets.dropna(axis=0, how='any', inplace=True)
    tweets.drop_duplicates('id', inplace=True)

    # make user id a string
    tweets['user'] = tweets['user'].map(lambda x: 'UID%019d' % x)

    # save utc and local times
    print(
        datetime.now().strftime('%Y-%m-%d %H:%M:%S -'),
        'Extracting time related features.'
    )
    tweets['utc_time'] = tweets['created_at'].map(
        lambda x: datetime.strptime(
            x, '%a %b %d %H:%M:%S +0000 %Y'
        ).replace(tzinfo=pytz.utc)
    )
    tweets['local_time'] = tweets.apply(
        lambda row: TIMEZONES[row['city']].normalize(row['utc_time']),
        axis=1
    )
    # tweets['local_hour'] = tweets['local_time'].map(lambda x: x.hour)
    tweets['weekday'] = tweets['local_time'].map(lambda x: x.weekday())
    tweets['month'] = tweets['local_time'].map(lambda x: x.month)

    # extract source
    print(
        datetime.now().strftime('%Y-%m-%d %H:%M:%S -'),
        'Extracting source.'
    )
    tweets['source'] = tweets['source'].map(
        lambda x: x.split('>')[1].split('<')[0].strip()
    )
    btm_95pct_sources = tweets['source'].value_counts()[
        tweets['source'].value_counts().cumsum()
        > tweets['source'].value_counts().sum() * 0.95
    ]
    for other in btm_95pct_sources.index:
        tweets['source'].replace({other: 'Other'}, inplace=True)

    print(
        datetime.now().strftime('%Y-%m-%d %H:%M:%S -'),
        'Extracting texts.'
    )
    tweets['text'].replace({r'\\s': ' '}, regex=True, inplace=True)

    # tokenize text
    tweets['words'] = tweets['text'].map(
        lambda x: [
            token.replace('#', '')
            for token in TWEET_TOKENIZER.tokenize(x)
            if is_word(token)
            ]
    )

    # count total words
    tweets['num_words'] = tweets['words'].map(len)
    # identify bad words
    tweets['badwords'] = tweets['words'].map(BAD_WORDS.find_badwords)
    # count bad words
    tweets['num_badwords'] = tweets['badwords'].map(len)

    tweets.drop(['created_at', 'id'], axis=1, inplace=True)

    return tweets

def main():
    """Run from CLI."""
    print(
        datetime.now().strftime('%Y-%m-%d %H:%M:%S -'),
        'Starting feature extraction process.'
    )
    files = glob.glob(READ_FILE_NAME+'*')
    tweets = pd.DataFrame()
    for f in files:
        tweets = tweets.append(pd.read_csv(f))
    print(
        datetime.now().strftime('%Y-%m-%d %H:%M:%S -'),
        'Raw files read.'
    )
    tweets = extract_features(tweets)
    print(
        datetime.now().strftime('%Y-%m-%d %H:%M:%S -'),
        'Writing features to a file.'
    )

    tweets['words'] = tweets['words'].map(';'.join)
    tweets['badwords'] = tweets['badwords'].map(';'.join)

    tweets.to_csv(WRITE_FILE_NAME, index=False)
    print(
        datetime.now().strftime('%Y-%m-%d %H:%M:%S -'),
        'Process completed.'
    )

if __name__ == '__main__':
    main()
