"""Utils."""
import re
import pytz

# Locations
CITIES = [
    'toronto',
    'new_york',
    'chicago',
    'los_angeles',
    'vancouver'
]

GEOCODES = [
    [43.6532, -79.3832, '25km'], # toronto
    [40.7128, -74.0060, '25km'], # new york
    [41.8781, -87.6298, '25km'], # chicago
    [34.0522, -118.2437, '25km'], # los angeles
    [49.2827, -123.1207, '25km'] # vancouver
]

SUBREDDIT_NAMES = {
    'toronto': 'toronto',
    'nyc': 'new_york',
    'chicago': 'chicago',
    'LosAngeles': 'los_angeles',
    'vancouver': 'vancouver'
}


# Timezones
TIMEZONES = {
    'toronto': pytz.timezone('America/Toronto'),
    'new_york': pytz.timezone('America/New_York'),
    'chicago': pytz.timezone('America/Chicago'),
    'los_angeles': pytz.timezone('America/Los_Angeles'),
    'vancouver': pytz.timezone('America/Vancouver')
}

def is_word(token):
    """Check if a token is a word including hashtags."""
    pattern = r'^(?!rt|https?://)(#?[\w]+)'
    return True if re.match(pattern, token) else False
