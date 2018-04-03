# pylint:disable=C0413, C0103
"""Get reddit comments."""
import os
import sys
sys.path.append(os.getcwd())
from datetime import datetime
import time
from dateutil.relativedelta import relativedelta
import yaml
import pandas as pd
import numpy as np
import praw
from src.utils import SUBREDDIT_NAMES

# delay 30 seconds after each RATE_LIMIT
DELAY = 30

RATE_LIMIT = 1000
# RATE_LIMIT = 10
FROM_DATE = datetime.today() - relativedelta(years=1)

COMMENT_COLUMNS = [
    'id', 'author', 'created_utc', 'subreddit',
    'score', 'ups', 'downs', 'gilded',
    'body', 'distinguished'
]

def main():
    """Run on CLI."""
    # query until FROM_DATE
    for subreddit in SUBREDDIT_NAMES:
        after_date = datetime.today()
        after = None
        while after_date > FROM_DATE:
            print(
                datetime.now().strftime('%Y-%m-%d %H:%M:%S -'),
                'Starting queries for', after_date
            )
            file_name = './data/rc_'\
                + subreddit + '_'\
                + datetime.now().strftime('%Y%m%d%H%M%S')\
                + '.csv'
            try:
                after = save_reddit_comments(subreddit, file_name, after)
                after_date = datetime.fromtimestamp(after.created_utc)
            except Exception as e:
                time.sleep(DELAY*5)
                print(e)
            if after is None:
                break
            time.sleep(DELAY)


def asdict(x):
    """Enable function mapping."""
    return x.__dict__

def save_reddit_comments(subreddit, file_name, after=None):
    """Query recent comments on submissions and save to csv."""
    with open('_access.yml', 'r') as f:
        reddit_access = yaml.load(f)['REDDIT']
        reddit_api = praw.Reddit(
            client_id=reddit_access['CLIENT_ID'],
            client_secret=reddit_access['CLIENT_SECRET'],
            user_agent=reddit_access['USER_AGENT']
        )

    if reddit_api.read_only:
        print(
            datetime.now().strftime('%Y-%m-%d %H:%M:%S -'),
            'API access successful.')

    df_all = pd.DataFrame()
    print(
        datetime.now().strftime('%Y-%m-%d %H:%M:%S -'),
        'Querying', subreddit, '...')
    subreddit_api = reddit_api.subreddit(subreddit)

    # paginate using after parameter
    if after:
        _submissions_generator = subreddit_api.new(
            limit=RATE_LIMIT,
            params={'after': after.fullname}
        )
    else:
        _submissions_generator = subreddit_api.new(limit=RATE_LIMIT)

    for ind, submission in enumerate(_submissions_generator):
        if np.mod(ind, 10) == 0:
            print(
                datetime.now().strftime('%Y-%m-%d %H:%M:%S -'),
                '...processing submission', '%06d' % ind, '...')
        _list_comments = submission.comments.list()
        if _list_comments:
            _df_comments = pd.DataFrame(list(map(asdict, _list_comments)))
            _df_comments = _df_comments[COMMENT_COLUMNS]
            df_all = df_all.append(_df_comments)
        after = submission

    try:
        # remove any duplicates
        df_all.drop_duplicates('id', inplace=True)
        # remove new lines from text
        df_all['body'].replace(
            r'[\r\n]+', r' ', regex=True, inplace=True
        )
        df_all.to_csv(file_name, index=False)
    except ValueError as e:
        print(e)
        print(
            datetime.now().strftime('%Y-%m-%d %H:%M:%S -'),
            'Terminating query for', subreddit
        )
        return None


    print(
        datetime.now().strftime('%Y-%m-%d %H:%M:%S -'),
        'Complete.')
    print(
        datetime.now().strftime('%Y-%m-%d %H:%M:%S -'),
        'Processed', df_all.shape[0], 'comments.')

    return after

if __name__ == '__main__':
    main()
