"""Scrap work."""
from src.utils.badwords import BadWords

badwords = BadWords()
badwords.get_badwords_full()
badwords.get_whitelist()
badwords.get_badwords()
badwords.add_whitelist(list('ab'))
badwords.remove_whitelist(['a', 'b'])

badwords.is_badword('shit')
badwords.find_badwords(['jungle', 'bunny', 'good', 'bunny', 'fudge', 'ass'])

[x for x in badwords.get_badwords_full() if ' ' in x]

import glob
import pandas as pd
from src.feature.extract_tweets import READ_FILE_NAME
from src.feature.extract_tweets import TWEET_TOKENIZER
from src.feature.extract_tweets import is_word
from src.feature.extract_tweets import extract_features


files = glob.glob(READ_FILE_NAME+'*')
tweets = pd.DataFrame()
for f in files:
    tweets = tweets.append(pd.read_csv(f))

tweets = extract_features(tweets)
sum(tweets['num_badwords'])
sum(tweets['num_words'])

tweets.describe()
tweets.select_dtypes(['object']).describe()
