"""Test script WIP."""
from datetime import datetime
import yaml
import pandas as pd
import numpy as np
import praw
from locations import SUBREDDIT_NAMES
# from src.data.locations import SUBREDDIT_NAMES

RATE_LIMIT = 100

POST_COLUMNS = [
    'id', 'author', 'created_utc', 'subreddit',
    'score', 'ups', 'downs', 'gilded', 'num_comments', 'over_18',
    'selftext', 'title'
]

COMMENT_COLUMNS = [
    'id', 'author', 'created_utc', 'subreddit',
    'score', 'ups', 'downs', 'gilded',
    'body'
]

FILE_NAME_SUFFIX = '_' + datetime.now().strftime('%Y%m%d%H%M') + '.csv'
FILE_NAME_POST = './data/reddit_posts' + FILE_NAME_SUFFIX
FILE_NAME_COMMENT = './data/reddit_comments' + FILE_NAME_SUFFIX

def main():
    """Run on CLI."""
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

    def asdict(x):
        """Enable function mapping."""
        return x.__dict__

    df_all_posts = pd.DataFrame(columns=POST_COLUMNS)
    df_all_comments = pd.DataFrame(columns=COMMENT_COLUMNS)
    for subreddit in SUBREDDIT_NAMES:
        print(
            datetime.now().strftime('%Y-%m-%d %H:%M:%S -'),
            'Querying', subreddit, '...')
        subreddit_api = reddit_api.subreddit(subreddit)
        _posts = []
        for ind, post in enumerate(subreddit_api.hot(limit=RATE_LIMIT)):
            if np.mod(ind, 10) == 0:
                print(
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S -'),
                    '...processing submission', '%04d' % ind, '...')
            _posts.append(post)
            _list_comments = post.comments.list()
            if len(_list_comments) > 0:
                _df_comments = pd.DataFrame(list(map(asdict, _list_comments)))
                _df_comments = _df_comments[COMMENT_COLUMNS]
                df_all_comments = df_all_comments.append(_df_comments)
        _df_posts = pd.DataFrame(list(map(asdict, _posts)))
        _df_posts = _df_posts[POST_COLUMNS]
        df_all_posts = df_all_posts.append(_df_posts)

    df_all_posts.drop_duplicates('id', inplace=True)
    df_all_comments.drop_duplicates('id', inplace=True)

    # remove new lines from text
    df_all_posts['selftext'].replace(r'\n', r'\s', regex=True, inplace=True)
    df_all_comments['body'].replace(r'\n', r'\s', regex=True, inplace=True)

    df_all_posts.to_csv(FILE_NAME_POST, index=False)
    df_all_comments.to_csv(FILE_NAME_COMMENT, index=False)
    print(
        datetime.now().strftime('%Y-%m-%d %H:%M:%S -'),
        'Complete.')
    print(
        datetime.now().strftime('%Y-%m-%d %H:%M:%S -'),
        'Processed', df_all_posts.shape[0],
        'posts and', df_all_comments.shape[0], 'comments.')
    # datetime.fromtimestamp(_post.created_utc)

if __name__ == '__main__':
    main()
