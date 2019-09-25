import re, json
import urllib.parse
import pandas as pd

from slackbot.bot import respond_to, listen_to
from slackbot import settings

TRY_TEXT_FETCH = "Try something like:\n`<@fido> fetch [keyword]`."""
with open(settings.FETCH_MAP_JSON) as f:
    FETCH_MAP = json.load(f)

class RecordNotFoundError(Exception):
    pass


@respond_to('fetch (.*)')
def fetch(message, fetch_key):
    text = message._body['text'].split(' ')
    if len(text) > 2:
        msg = "I couldn't understand your fetch query. The fetch key " + \
            "should be exactly one word with no spaces.\n"
    else:
        try:
            msg = "Woof! I've fetched `{}` for you.\n{}".format(fetch_key, FETCH_MAP[fetch_key])
        except KeyError:
            msg = "I couldn't find any item keyed by `{}`. ".format(fetch_key) + TRY_TEXT_FETCH
    message.reply(msg, in_thread=True)