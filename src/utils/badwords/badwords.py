"""Bad word lists"""
from .wordlists import BADWORDS01, BADWORDS02, BADWORDS03

class BadWords():
    """Helper for checking against a bag of badwords."""
    def __init__(self):
        self._fullset = set(
            BADWORDS01 + BADWORDS02 + BADWORDS03
        )
        self._whitelist = set([
            'god',
            'bell',
            'bloody',
            'breasts',
            'cracker',
            'gay',
            'git',
            'knob',
            'wang',
            'willy',
            'lust',
            'lusting',
            'lesbian'
        ])

    def _get_badwords_full(self):
        """Return the full set of bad words."""
        return self._fullset

    def _get_badwords(self):
        """Return the set of bad words excluding white list."""
        return self._fullset & set(self._fullset ^ self._whitelist)

    def get_whitelist(self):
        """Return the set of whitelist."""
        return self._whitelist

    def get_badwords_full(self):
        """Return the full set of bad words."""
        return self._get_badwords_full()

    def get_badwords(self):
        """Return the set of bad words excluding white list."""
        return self._get_badwords()

    def is_badword(self, word):
        """Check if a word is in the list."""
        if isinstance(word, str):
            return word.lower() in self._get_badwords()
        raise ValueError('Invalid input type.')

    def find_badwords(self, words):
        """Check if bad words from a list of wrds."""
        _badwords = self._get_badwords()
        _composite_badwords = [
            bad for bad in _badwords
            if ' ' in bad
        ]
        _words = ' '.join([word.lower() for word in words])
        if isinstance(words, list):
            _composite_found = [
                bad for bad in _composite_badwords
                if bad in _words
            ]
            for comp in _composite_found:
                _words = _words.replace(comp, '')
            _single_found = [
                word for word in _words.split(' ')
                if word in _badwords
            ]
            return _composite_found + _single_found
        raise ValueError('Invalid input type.')

    def print_badwords(self, words):
        """Return a concated list of bad words found separated by ;."""
        _found = self.find_badwords(words)
        return ';'.join(_found)

    def add_whitelist(self, word):
        """Add a string or a list of strings to whitelist."""
        if isinstance(word, str):
            self._whitelist.update(word)
            return True
        elif isinstance(word, list):
            _word_list = [x for x in word]
            self._whitelist.update(word)
            return True
        raise ValueError('Invalid input type.')

    def remove_whitelist(self, word):
        """Remove a string or a list of strings from whitelist."""
        if isinstance(word, str):
            try:
                self._whitelist.remove(word)
                return True
            except KeyError:
                print(word, 'not found in whitelist.')
                return False
        if isinstance(word, list):
            for x in word:
                try:
                    self._whitelist.remove(str(x))
                except KeyError:
                    print(x, 'not found in whitelist.')
                    return False
            return True
        raise ValueError('Invalid input type.')
