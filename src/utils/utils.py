"""Utils."""
import pytz

# Timezones
TIMEZONES = {
    'toronto': pytz.timezone('America/Toronto'),
    'new_york': pytz.timezone('America/New_York'),
    'chicago': pytz.timezone('America/Chicago'),
    'los_angeles': pytz.timezone('America/Los_Angeles'),
    'vancouver': pytz.timezone('America/Vancouver')
}
