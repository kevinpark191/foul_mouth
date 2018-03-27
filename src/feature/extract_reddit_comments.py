"""Extract features from reddit comments."""
from datetime import datetime
import glob
import pytz
import pandas as pd

READ_FILE_NAME = './data/reddit_comments_'
WRITE_FILE_NAME = './data/feat_reddit_comments_' \
    + datetime.now().strftime('%Y%m%d%H%M') + '.csv'

def main():
    """Run from CLI."""
    files = glob.glob(READ_FILE_NAME+'*')
    files.sort()
    reddit_comments = pd.read_csv(files[-1])

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
    # not able to extract local (submitter's) time
    reddit_comments['utc_time'] = reddit_comments['created_utc'].map(
        lambda x: datetime.fromtimestamp(x).replace(tzinfo=pytz.utc)
    )
    reddit_comments['weekday'] = reddit_comments['utc_time'].map(
        lambda x: x.weekday()
    )
    reddit_comments['month'] = reddit_comments['utc_time'].map(
        lambda x: x.month
    )

    # TODO: tokenize body

    reddit_comments.drop(['index', 'created_utc', 'id', ])

    reddit_comments.to_csv(WRITE_FILE_NAME)

if __name__ == '__main__':
    main()
