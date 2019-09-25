# -*- coding: utf-8 -*-

import os, json
import datetime
import pytz

PLUGINS = [
    'slackbot.plugins',
]

ERRORS_TO = None
DEBUG = False

### Config values to change ###
BOT_SLACK_ID = "ULXP4MAUS" # Slack ID of bot
CONFIG_JSON = "config/config.json" # Path to config.json
FETCH_MAP_JSON = "config/fetch_map.json" # Path to fetch_map.json
PIAZZA_BOT_LAST_DAYS = 7 # Get Piazza questions from last N number of days
### End config values to change

if DEBUG:
    now = datetime.datetime.now()
    PIAZZA_PAGER_REFRESH_TOD = [(now + datetime.timedelta(seconds=9)).strftime("%H:%M:%S")]
else:
    PIAZZA_PAGER_REFRESH_TOD = ["{:02d}:00:00".format(h) for h in [14, 22]]

# Default reply used when no command is matched
DEFAULT_REPLY = "I'm Fido, the friendly dog that fetches your data! Ask me for...\n" + \
    "*Student info:* `@fido whois [student name|email|SID]`\n" + \
    "*Staff info:* `@fido whois [staff name|email|@slack|lab ###]`\n" + \
    "*Item fetch:* `@fido fetch [keyword (e.g. roster, la_attendance...)]`"

TIMEOUT = 100 # Setup timeout for slacker API requests (e.g. uploading a file).
COLOR_RED = "#d4372f"
COLOR_YELLOW = "#dbdb40"

class Config(object):
    """ Stores all info from config.json"""
    def __init__(self):
        with open(CONFIG_JSON) as f:
            self.__dict__ = json.load(f)

CONFIG = Config()
BOT_NAME = CONFIG.bot_name

'''
Setup a comma delimited list of aliases that the bot will respond to.

Example: if you set ALIASES='!,$' then a bot which would respond to:
'botname hello'
will now also respond to
'$ hello'
'''
ALIASES = ''

'''
If you use Slack Web API to send messages (with
send_webapi(text, as_user=False) or reply_webapi(text, as_user=False)),
you can customize the bot logo by providing Icon or Emoji. If you use Slack
RTM API to send messages (with send() or reply()), or if as_user is True
(default), the used icon comes from bot settings and Icon or Emoji has no
effect.
'''
# BOT_ICON = 'http://lorempixel.com/64/64/abstract/7/'
# BOT_EMOJI = ':godmode:'

for key in os.environ:
    if key[:9] == 'SLACKBOT_':
        name = key[9:]
        globals()[name] = os.environ[key]

try:
    from slackbot_settings import *
except ImportError:
    try:
        from local_settings import *
    except ImportError:
        pass

# convert default_reply to DEFAULT_REPLY
try:
    DEFAULT_REPLY = default_reply
except NameError:
    pass
