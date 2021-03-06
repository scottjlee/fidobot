from piazza_api import Piazza
from slacker import Slacker
from time import sleep
from slackbot import settings
from slackbot.settings import CONFIG
from collections import defaultdict as ddict
import html
import sys, os
from datetime import datetime
import pytz
from pytz import timezone

"""
The Piazza (bootleg) API response has the following structure:
{
	'fol': 'logistics|', 
	'pin': 1, # bool for pinned
	'm': 1566749524338, 
	'rq': 0, 
	'id': 'jzpwiwuhpyq3q0', # post id?
	'log': [
		{'t': '2019-08-24T18:53:04Z','u': 'i25hx8fdvmy2cq', 'n': 'create'}, 
		{'t': '2019-08-24T18:53:08Z', 'u': 'i25hx8fdvmy2cq', 'n': 'update'}, 
		{'t': '2019-08-25T16:10:17Z', 'u': 'jzkuzgmz5ra6jy', 'n': 'followup'}, 
		{'t': '2019-08-25T16:12:04Z', 'u': 'jzkuzgmz5ra6jy', 'n': 'feedback'}
	], 
	'unique_views': 210, 
	'score': 210.0, 
	'is_new': False, 
	'version': 2, 
	'bucket_name': 'Pinned', 
	'bucket_order': 0, 
	'folders': ['logistics'], # folder/tags
	'nr': 21,  # post number/ID
	'main_version': 4, 
	'request_instructor': 0, 
	'subject': 'Welcome to Data 8 &#43; First Lecture/Course Logistics!', 
	'no_answer_followup': 0, 
	'num_favorites': 3, 
	'type': 'note', 
	'tags': ['instructor-note', 'logistics', 'pin'], 
	'tag_good_prof': 1, 
	'content_snipet': 'Welcome to Data 8! The course staff and co-instructors, Ramesh Sridharan and Swupnil Sahai, are so excited to have the c', 
	'view_adjust': 0, 
	'modified': '2019-08-25T16:12:04Z', 
	'gd': 5, 
	'updated': '2019-08-24T18:53:04Z', 
	'status': 'active'
}
"""

p = Piazza()
p.user_login(email=CONFIG.piazza_email, password=CONFIG.piazza_password)
network = p.network(CONFIG.piazza_id)
bot=Slacker(CONFIG.slack_api_token) 


### SETUP PARAMETERS TO CHANGE ###

if settings.DEBUG:
	tag_to_channel_map = {"other": ["test-fido"]}
else:
	tag_to_channel_map = {
		"logistics": ["team-logistics"],
		"grading": ["team-grading"],
		"jupyter": ["team-content-infra"]
	}
	for prefix, max_num in [('hw', 10), ('lab', 12), ('project', 3)]:
		for n in range(1, max_num + 1):
			tag_name = "{}{}".format(prefix, n)
			tag_to_channel_map[tag_name] = ['team-pedagogy', 'team-content-infra']

forever_post_nums = set([141, 142])

### END SETUP PARAMETERS TO CHANGE ###

# URL for posts on the page
POST_BASE_URL = "https://piazza.com/class/{}?cid=".format(CONFIG.piazza_id)
FEED_LIMIT = 200  # Max number of posts to pull from feed

def get_max_id(feed):
	for post in feed:
		if "pin" not in post:
			return post["nr"]
	return -1

last_id = 6
def check_for_new_posts():
	global last_id
	try:
		feed = network.get_feed(limit=FEED_LIMIT)['feed']
		updated_last_id = get_max_id(feed)
		if updated_last_id > last_id:
			channel_to_atmt, channel_post_info = process_feed(feed, last_id, updated_last_id)
			for channel, attachments in channel_to_atmt.items():
				for info_item in ("unanswered", "unresolved"):
					if info_item not in channel_post_info[channel]:
						channel_post_info[channel][info_item] = 0
				if "tags" not in channel_post_info[channel]:
					channel_post_info[channel]["tags"] = set()
				tags_str = "["
				for tag in channel_post_info[channel]["tags"]:
					tags_str += "`{}`, ".format(tag)
				tags_str = tags_str[:-2] + "]"
				message = "There are currently *{} unanswered posts* / *{} unresolved threads* with tags {}".format(
						channel_post_info[channel]["unanswered"],
						channel_post_info[channel]["unresolved"],
						tags_str,
					)
				try:
					bot.chat.post_message(
						channel,
						message, 
						as_user=settings.BOT_NAME,
						attachments=attachments,
					)
				except Exception as e:
					print(channel, e)
			last_id = updated_last_id
		else:
			pass
		if settings.DEBUG:
			print("Sleep piazza-pager")
	except Exception as e:
		if settings.DEBUG:
			print("Error when attempting to get Piazza feed, going to sleep...")
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print("Error:", exc_type, fname, exc_tb.tb_lineno)

def is_valid_new_post(post, post_start_nr, post_end_nr):
	tags = post["tags"]
	def not_in_tags(tags, lst):
		for x in lst:
			if x in tags:
				return False
		return True
	if post["nr"] <= 5:  # First 5 posts are Piazza-defaults
		return False
	if post["nr"] in forever_post_nums:
		return True
	post_created_ts = datetime.strptime(post['log'][0]['t'], "%Y-%m-%dT%H:%M:%SZ").astimezone(timezone('US/Pacific'))
	curr_ts = datetime.now(tz=pytz.utc).astimezone(timezone('US/Pacific'))
	if (curr_ts - post_created_ts).days > settings.PIAZZA_BOT_LAST_DAYS:  # only return posts within last week
		return False
	# TODO: keep questions that are answered but with unresolved followups
	return post_start_nr < post["nr"] and post["nr"] < post_end_nr \
		and "unanswered" in tags and "note" not in tags

def process_feed(feed, post_start_nr, post_end_nr):
	channel_to_response = ddict(list) # Stores channel -> [{response}, {response}, ...]
	# Stores channel -> {"unanswered": int, "unresolved": int, "tags": set(str, str, ...)}
	channel_post_info = ddict(dict) 
	
	num_unanswered, num_unresolved = 0, 0
	for post in feed:
		curr_folders, curr_channels = post["folders"], set()
		for folder in curr_folders:
			try:
				channels_to_add = tag_to_channel_map[folder]
				for curr_channel in channels_to_add:
					curr_channels.add(curr_channel)
			except KeyError:
				pass
		
		if len(curr_channels) == 0:  # No matching channels to post in
			continue

		attachments = []
		if is_valid_new_post(post, post_start_nr, post_end_nr):
			subject_preview = post["subject"]
			if len(subject_preview) > 30:
				subject_preview = subject_preview[:30] + "..."
			title = "@{} - {}".format(post["nr"], subject_preview)


			
			for channel in curr_channels:
				if 'unanswered' not in post["tags"] and \
				post["no_answer_followup"] == 0:
					continue 

				if 'unanswered' in post["tags"]:
					if "unanswered" not in channel_post_info[channel]:
						channel_post_info[channel]["unanswered"] = 0
					channel_post_info[channel]["unanswered"] += 1

				if post["no_answer_followup"] > 0:
					if "unresolved" not in channel_post_info[channel]:
						channel_post_info[channel]["unresolved"] = 0
					channel_post_info[channel]["unresolved"] += post["no_answer_followup"]
					title += " - {} followups".format(post["no_answer_followup"])
				post_url = "{}{}".format(POST_BASE_URL, post["nr"])
				post_atcmt = {
					"fallback": title,
					"title": title,
					"title_link": post_url,
					"text": html.unescape(post["content_snipet"]) + "...",
					"color": settings.COLOR_RED,
					'actions': [{
						"type": "button",
						"text": "View",
						"url": post_url
					}]
				}

				if channel not in channel_to_response:
					channel_to_response[channel] = []
				channel_to_response[channel].append(post_atcmt)
				if channel not in channel_post_info:
					channel_post_info[channel] = {}

				if "tags" not in channel_post_info[channel]:
					channel_post_info[channel]["tags"] = set()
					
				for tag in post["folders"]:
					if tag in tag_to_channel_map:
						for c in tag_to_channel_map[tag]:
							if c == curr_channel:
								channel_post_info[channel]["tags"].add(tag)
	return channel_to_response, channel_post_info