"""Scrap work."""
from src.utils.badwords import BadWords

badwords = BadWords()
badwords.get_badwords_full()
badwords.get_whitelist()
badwords.get_badwords()

with open('badlist', 'w') as f:
    f.write('\n'.join(badwords.get_badwords_full()))

with open('whitelist', 'w') as f:
    f.write('\n'.join(badwords.get_whitelist()))
