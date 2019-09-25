import re
import urllib.parse
import pandas as pd

from slackbot.bot import respond_to, listen_to
from slackbot.settings import CONFIG

TRY_TEXT_WHOIS = "Try something like:\n`<@fido> whois " + \
    "[student name|email|SID]` or `<@fido> whois " + \
    "[staff name|email|lab ###]`."""
roster_student = pd.read_csv(CONFIG.roster_student, dtype=str)
roster_staff = pd.read_csv(CONFIG.roster_staff, dtype=str)

LAB_BUILDINGS = ["evans", "cory", "sdh"]

class RecordNotFoundError(Exception):
    pass


def build_info_output_student(info_dict_list):
    attachments = []

    for info_dict in info_dict_list:
        attachment = {
            'fallback': "",
            'fields': [
                {
                    "title": "Name",
                    "value": info_dict["Name"],
                    "short": True,
                },
                {
                    "title": "Role",
                    "value": "Student",
                    "short": True,
                },
                {
                    "title": "Email",
                    "value": info_dict['Email Address'],
                    "short": True,
                },
                {
                    "title": "SID",
                    "value": info_dict['Student ID'],
                    "short": True,
                },
                {
                    "title": "Lab GSI",
                    "value": get_lab_gsi(info_dict["LAB"]),  # TODO: Lab TA
                    "short": True
                },
            ],
            'color': '#764FA5',
            'text': "",
            'actions': [{
                "type": "button",
                "text": "OK Admin",
                "url": info_dict['ok_url']
            }],
        }
        attachments.append(attachment)

    msg = "Woof! Here's the requested information"
    if len(info_dict_list) > 1:
        msg += ". There are *{} possible matches*".format(len(info_dict_list))
    msg += ":"
    return msg, attachments


def build_info_output_staff(info_dict_list, short_output):
    attachments = []

    for info_dict in info_dict_list:
        lab_str = "LAB {} - {} - {}".format(
            info_dict["Lab Number"],
            info_dict["Lab Time"],
            info_dict["Lab Room"],
        )

        curr_attachment = {
            'fallback': "",
            'fields': [
                {
                    "title": "Name",
                    "value": info_dict['Name'],
                    "short": True,
                },
                
                {
                    "title": "Lab Section",
                    "value": lab_str,  # TODO: Lab section
                    "short": True
                },
            ],
            'color': '#764FA5',
            'text': "",
        }
        if not short_output:
            curr_attachment["fields"].extend([
                {
                    "title": "Role",
                    "value": info_dict['Role'],
                    "short": True,
                },
                {
                    "title": "Email",
                    "value": info_dict['Email Address'],
                    "short": False,
                },
                {
                    "title": "Groups",
                    "value": info_dict['Groups'],
                    "short": False,
                },
            ])

        attachments.append(curr_attachment)
    msg = "Woof! Here's the requested information"
    if len(info_dict_list) > 1:
        msg += ". There are *{} possible matches*".format(len(info_dict_list))
    msg += ":"
    return msg, attachments


def get_info(key, key_column, short_output=False):
    """ This function does the heavy lifting. Given a key value
    and the column name (e.g. a student's email), returns the
    rest of the missing information as a dictionary. """
    tables = [("student", roster_student), ("staff", roster_staff)]
    for (df_name, df) in tables:
        possible_queries = [key]
        if key_column == 'Name':  # Add flipped last/first name
            name = key.split(', ')
            if len(name) == 1:
                name = key.split(' ')
            if len(name) == 1:
                raise RecordNotFoundError("Could not parse name `{}`".format(name))

            if df_name == 'student':
                name_query = '{}, {}'.format(name[1], name[0])
            elif df_name == 'staff':
                name_query = '{} {}'.format(name[0], name[1])
            possible_queries.append(name_query)

        matches_dicts = []
        for query_key in possible_queries:
            try:
                known_filter = (df[key_column].str.lower() == query_key.lower())
            except KeyError:
                break
            if sum(known_filter) > 0:
                matching_rows = df[known_filter]
                for _, row in matching_rows.iterrows():
                    row_dict = row.to_dict()
                    encoded_email = urllib.parse.quote(row_dict['Email Address'])
                    row_dict['ok_url'] = '{}{}'.format(CONFIG.ok_link, encoded_email)
                    matches_dicts.append(row_dict)

                if df_name == 'student':
                    return build_info_output_student(matches_dicts)
                elif df_name == 'staff':
                    return build_info_output_staff(matches_dicts, short_output)

    raise RecordNotFoundError(
        "Could not find key(s) `{}` in column `{}` from tables {}"\
            .format(possible_queries, key_column, [t[0] for t in tables]))


def clean_arg(arg):
    return re.sub("(,|')", '', arg).lower().strip()


def get_lab_gsi(lab_num):
    match = roster_staff[roster_staff["Lab Number"] == lab_num].iloc[0]
    return match["Name"]


@respond_to('whois')
def info_parse(message):
    text = message._body['text']
    tokens = text.split(" ")[1:]  # Remove 'whois' from tokens

    if len(tokens) >= 1:
        arg1 = clean_arg(tokens[0]) 
        if arg1 == 'help':
            message.reply("I can fetch student or staff data." + TRY_TEXT_WHOIS,
            in_thread=True)
            return
    else:
        message.reply("Sorry, I couldn't understand your query format. " + TRY_TEXT_WHOIS,
        in_thread=True)
        return
    if len(tokens) >= 2:
        arg2 = clean_arg(tokens[1])
    if len(tokens) >= 3:
        arg3 = clean_arg(tokens[2])
    
    try:
        if arg1 == "teaching": 
            try:
                if arg2.upper() in ("W", "T", "F"):  # lab time
                    lab_time = "{} {}".format(arg2.upper(), arg3)
                    msg, attachments = get_info(
                        key=lab_time, 
                        key_column="Lab Time", 
                        short_output=True,
                    )
                else:  # lab location 
                    msg, attachments = get_info(
                        key=arg2, 
                        key_column="Lab Room", 
                        short_output=True,
                    )
            except UnboundLocalError:  # no second arg specified, default to their own
                msg, attachments = "Please specify a lab time or room.", None
        elif len(arg1) == 3 and any([r in tokens for r in LAB_BUILDINGS]) \
            and int(arg1) > 100 and int(arg1) < 150:  # lab number
            msg, attachments = get_info(key=arg1, key_column="Lab Number")
            
        elif '@' in arg1 and '|' in arg1:  # Email
            email_start = arg1.find('|')
            email = arg1[email_start + 1:-1]
            msg, attachments = get_info(key=email, key_column='Email Address')
        elif re.match(r'^[1-9][0-9]{7,9}$', arg1):  # SID
            msg, attachments = get_info(key=arg1, key_column='Student ID')
        else:  # Name
            if len(tokens) >= 3:
                last, first = tokens[-1], " ".join(tokens[:-1])
            else:
                last, first = arg1, arg2
            msg, attachments = get_info(key="{}, {}".format(last, first), key_column='Name')
    except RecordNotFoundError as e:
        msg, attachments = str(e), None
        message.reply("Sorry, I couldn't find anything that matches your query key. " + TRY_TEXT_WHOIS,
        in_thread=True)

    message.reply_webapi(msg, attachments=attachments, in_thread=True)

    
@respond_to("groupshout (.*)")
def groupshout(message, group_key):
    group_key = group_key.split()[0]  # grab first word after groupshout
    if group_key[0] == "@":
        group_key = group_key[1:]
    if group_key[-1] == "s":  # get rid of plural
        group_key = group_key[:-1]

    shout_str = "groupshout `{}`: ".format(group_key)
    total_count = 0
    group_key = group_key.lower()
    for i, staff in roster_staff.iterrows():
        if group_key in staff["Groups"].lower() or \
            group_key in (
                str(staff["Lab Room"]).lower(), 
                str(staff["Lab Time"]).lower()
            ):
            shout_str += "<@{}> ".format(staff["Slack IDN"])
            total_count += 1
    if total_count == 0:
        shout_str = "Could not find a group with key `{}`.".format(group_key)
    message.reply(shout_str, in_thread=True)
