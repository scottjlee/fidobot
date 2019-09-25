from slackbot import settings
import slack
from slackbot.bot import respond_to, listen_to  # lol circular import fix


import re
import datetime
import pytz
from pytz import timezone


slack_token = settings.CONFIG.slack_api_token
client = slack.WebClient(token=slack_token)

end_ts_to_message_infos = {}

def get_channel_members(channel_id):
	""" Slack channel id -> [member IDs] """
	channel_info = client.groups_info(channel=channel_id)
	members = channel_info["group"]["members"]
	members.remove(settings.BOT_SLACK_ID)
	return members

def get_reacted_users(channel_id, msg_creation_ts):
	reacted_users = set()
	try:
		response = client.reactions_get(channel=channel_id, timestamp=msg_creation_ts)
	except Exception as e:
		print("ERROR:", e)
		return reacted_users, ""
	response_type = response["type"]
	if "reactions" not in response[response_type]:
		return reacted_users, ""
	
	reactions = response[response_type]["reactions"]
	for react_type in reactions:
		for reacted_user in react_type["users"]:
			reacted_users.add(reacted_user)
	message_author = response[response_type]["user"]
	return reacted_users, message_author

@respond_to('(.\n)*reactcheck(.\n)*')
def reactcheck(message, pretext, react_text, posttext=None):
	""" Exact time format: HH:MM[am/pm] [today|tonight|tomorrow|MM/DD]"""
	text = message._body['text']
	start_ind = text.index("reactcheck")
	text = text[start_ind:]

	match_pattern = re.compile("reactcheck ((\d{1,2}:\d{1,2})(am|pm)|midnight|noon) ((\d{1,2}\/\d{1,2})|(today)|(tonight)|(tomorrow))")
	groups = match_pattern.match(text)
	
	days_delta = 0
	tod = groups.group(1)

	if tod == "midnight":
		days_delta += 1
		tod, ampm = "12:00", "am"
		day = groups.group(4)
	elif tod == "noon":
		tod, ampm = "12:00", "pm"
		day = groups.group(4)
	else:
		tod, ampm = tod[:-2], tod[-2:]
		day = groups.group(4)
	
	now = datetime.datetime.now(tz=pytz.utc).astimezone(timezone('US/Pacific'))
	if day in ("today", "tonight"):
		day = now
	elif day == "tomorrow":
		day = now + datetime.timedelta(days=1)
	else:
		ind = day.index("/")
		day = now.replace(
			month=int(day[:ind]),
			day=int(day[ind+1:]),
		).astimezone(timezone('US/Pacific'))

	split_time = tod.split(":")
	hm = day.replace(
		hour=(int(split_time[0]) + (12 if ampm == "pm" else 0)) % 24, 
		minute=int(split_time[1]),
	)
	
	final_date = (hm + datetime.timedelta(days=days_delta))
	if final_date < now:
		message.reply("ERROR: Due time cannot be earlier than now.", in_thread=True)
		return
	date = final_date.strftime("%m/%d")

	ts = datetime.datetime.strptime("{} {}{}".format(date, tod, ampm), "%m/%d %I:%M%p")
	final_ts = ts.replace(year=now.year)

	# Get list of channel member IDs
	channel_id = message.channel._body["id"]
	members = get_channel_members(channel_id)

	if final_ts not in end_ts_to_message_infos:
		end_ts_to_message_infos[final_ts] = []
	end_ts_to_message_infos[final_ts].append({
		"channel_id": channel_id, 
		"creation_ts": message._body["ts"], 
	})
	return members

def check_for_reacts(curr_ts):
	curr_infos = end_ts_to_message_infos.pop(curr_ts)
	for info in curr_infos:
		reacted_users, message_author = get_reacted_users(info["channel_id"], info["creation_ts"])
		channel_members = get_channel_members(info["channel_id"])
		if len(reacted_users) == len(channel_members):
			msg_text = "<@{}>: All members have reacted to this thread.".format(message_author)
		else:
			msg_text = "Reminding the following people who haven't reacted to this post yet:"
			
			for user_id in channel_members:
				if user_id not in reacted_users:
					msg_text += " <@{}>".format(user_id)

		client.chat_postMessage(
			channel=info["channel_id"],
			text=msg_text,
			thread_ts=info["creation_ts"],
			as_user=False,
			username=settings.BOT_NAME
		)
