# pylint:disable=C0413
"""Extract features from reddit comments."""
import os
import sys
sys.path.append(os.getcwd())
from datetime import datetime
import glob
import pytz
import pandas as pd
from nltk.tokenize import TweetTokenizer
from src.utils import SUBREDDIT_NAMES, TIMEZONES, is_word
from src.utils.badwords import BadWords

READ_FILE_NAME = './data/rc_'
WRITE_FILE_NAME = './data/feat_rc_'\
    + datetime.now().strftime('%Y%m%d%H%M') + '.csv'

# use nltk TweetTokenizer to
# 1) tokenize urls
TWEET_TOKENIZER = TweetTokenizer(
    preserve_case=False,
    reduce_len=True
)

# bad word identifier
BAD_WORDS = BadWords()

def extract_features(reddit_comments):
    """Extract features."""
    # drop duplicates, missing values, and deleted/removed comments
    reddit_comments = reddit_comments[
        reddit_comments['body'].map(
            lambda x: x not in ['[deleted]', '[removed]']
        )
    ].reset_index()
    # author: null if this is a promotional link
    reddit_comments.dropna(axis=0, inplace=True, subset=['body', 'author'])
    reddit_comments.drop_duplicates('id', inplace=True)

    # save utc time
    reddit_comments['utc_time'] = reddit_comments['created_utc'].map(
        lambda x: datetime.fromtimestamp(x).replace(tzinfo=pytz.utc)
    )
    # not able to extract local (submitter's) time
    # assume same timezones as the subreddit city
    reddit_comments['local_time'] = reddit_comments.apply(
        lambda row: TIMEZONES[SUBREDDIT_NAMES[row['subreddit']]].normalize(
            row['utc_time']
        ), axis=1
    )
    reddit_comments['weekday'] = reddit_comments['local_time'].map(
        lambda x: x.weekday()
    )
    reddit_comments['month'] = reddit_comments['local_time'].map(
        lambda x: x.month
    )

    # remove new lines from comments
    print(
        datetime.now().strftime('%Y-%m-%d %H:%M:%S -'),
        'Extracting texts.'
    )
    reddit_comments['body'].replace({r'\\s': ' '}, regex=True, inplace=True)

    # tokenize body
    reddit_comments['words'] = reddit_comments['body'].map(
        lambda x: [
            token
            for token in TWEET_TOKENIZER.tokenize(x)
            if is_word(token)
        ]
    )
    # count total words
    reddit_comments['num_words'] = reddit_comments['words'].map(len)
    # ientify bad words
    reddit_comments['badwords'] = reddit_comments['words'].map(
        BAD_WORDS.find_badwords
    )
    # count bad words
    reddit_comments['num_badwords'] = reddit_comments['badwords'].map(len)

    reddit_comments.drop(
        ['index', 'created_utc', 'id', 'body'], axis=1, inplace=True
    )
    return reddit_comments

def main():
    """Run from CLI."""
    print(
        datetime.now().strftime('%Y-%m-%d %H:%M:%S -'),
        'Starting feature extraction process.'
    )
    files = glob.glob(READ_FILE_NAME+'*')
    reddit_comments = pd.DataFrame()
    for f in files:
        reddit_comments = reddit_comments.append(pd.read_csv(f))

    reddit_comments = extract_features(reddit_comments)

    reddit_comments.to_csv(WRITE_FILE_NAME)

if __name__ == '__main__':
    main()
