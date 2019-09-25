# Fido: a friendly Slackbot for teaching staff support

Fido is a Slackbot that has a variety of features to assist teaching staff members. Some main features include:
- [Student/Staff roster lookup](https://github.com/scottjlee/fidobot#features-overview)
- [Information recall](https://github.com/scottjlee/fidobot#fetch-get-commonly-used-information)
- [Group tagging](https://github.com/scottjlee/fidobot#groupshout-tag-entire-groups-of-staff-members)
- [Piazza paging](https://github.com/scottjlee/fidobot#piazza-pager-channel-specific-digest-of-unanswered-piazza-posts)
- [Timed action item reminder](https://github.com/scottjlee/fidobot#reactcheck-timed-action-item-reminders)

### How can I use Fido for my course?
Check out [setup instructions](https://github.com/scottjlee/fidobot/blob/master/SETUP.md). Once that's done, simply add Fido to your desired Slack channel by clicking on the channel name, then "Add an app" where you will be able to find the `Fido Bot` app. You can also DM Fido under the `Apps` section of the sidebar.

### Quick Cheatsheet
- Look up a student on the roster: `@fido whois [student name|email|SID]`
- Look up a staff member on the roster: `@fido whois [staff name|email|SID]`
- Look up all staff members for a lab number/time/room: `@fido whois teaching [Lab number|Lab location|Lab time]`
- Get information (e.g. links) by key word: `@fido fetch [keyword]`
- Tag a group by group name: `@fido groupshout [group name]`
- Set up a timed action item reminder: `@fido [pretext...] reactcheck [time] [date] [posttext...]`

# Features Overview

## `whois`: student/staff roster lookup
- Look up a student on the roster: `@fido whois <student_key>`
  - `student_key`: one of student name, email, SID
  
![](https://github.com/scottjlee/fidobot/blob/master/docs/whois-student.png) 

- Look up a staff member on the roster: `@fido whois <staff_key>`
  - `staff_key`: one of staff name, email, Lab number, Lab location, Lab time

![](https://github.com/scottjlee/fidobot/blob/master/docs/whois-staff.png) 

- Note that you can get all the staff members teaching in a certain room:

![](https://github.com/scottjlee/fidobot/blob/master/docs/whois-teaching-room.png)

- The same with the lab time:

![](https://github.com/scottjlee/fidobot/blob/master/docs/whois-teaching-time.png)

## `fetch`: get commonly used information 
- Get information (e.g. links) by key word: `@fido fetch <keyword>`
  - You can view all of the currently available keywords and their corresponding information in [config/fetch_map.json](https://github.com/scottjlee/fidobot/blob/master/config/fetch_map.json). Please make a pull request to add more items to this mapping.

![](https://github.com/scottjlee/fidobot/blob/master/docs/fetch.png)

## `groupshout`: tag entire groups of staff members
- Tag a group by group name: `@fido groupshout <group_name>`
  - The currently supported list of group names is: `gsi`, `gsi-returning`, `gsi-new`, `tutor`, `tutor-returning`, `tutor-new`, `lead`, `professor`.

![](https://github.com/scottjlee/fidobot/blob/master/docs/groupshout-group.png)

![](https://github.com/scottjlee/fidobot/blob/master/docs/groupshout-group2.png)

- You can also groupshout by lab time or location:

![](https://github.com/scottjlee/fidobot/blob/master/docs/groupshout-time.png)

![](https://github.com/scottjlee/fidobot/blob/master/docs/groupshout-room.png)

## `piazza-pager`: channel-specific digest of unanswered Piazza posts 
- This feature automatically alerts channels with the set of unanswered Piazza posts on a channel-by-channel basis. For example, questions with the `logistics` tag would be sent to the logistics channel.
- Currently, this is done [two times](https://github.com/scottjlee/fidobot/blob/8e6c329604bf375ab6f7660600cb6ef20dc75365/slackbot/settings.py#L23) a day: 2 PM and 10 PM.
- Once you resolve a Piazza question, you can delete it from Fido's feed by pressing the "x" (this will update Fido's feed for all users globally).
- The current mapping of Piazza tags to Slack channels is [here](https://github.com/scottjlee/fidobot/blob/8e6c329604bf375ab6f7660600cb6ef20dc75365/slackbot/plugins/piazza_pager.py#L57).

![](https://github.com/scottjlee/fidobot/blob/master/docs/piazza-pager.png)

## `reactcheck`: timed action item reminders
- Set up a `reactcheck`: `@fido reactcheck [time] [date]`
  - `time`: follows one of the following formats: `noon` OR `midnight` OR `[H]H:MM[am|pm]`
  - `date`: follows one of the following formats: `today` OR `tonight` OR `tomorrow` OR `[M]M/[D]D`
- This feature allows you to send out important announcements that need to be read or have action items due at some future time. For example, filling out a Google form by tonight. 
- Note that you can have text (e.g. the actual "announcement" you want people to read) before and after the `reactcheck` call. **However, the message MUST start with a tag to `@fido`.**
- If all users react to a post before the designated deadline, then Fido will tag the original user who created the post once time is up to let them know that everyone completed the action items.

### Examples
All of these examples were run in a channel with two users, @scott and @annie.

- `reactcheck`s both users because they did not react:
![](https://github.com/scottjlee/fidobot/blob/master/docs/reactcheck-1.png)

- `reactcheck`s only the users who have not reacted:
![](https://github.com/scottjlee/fidobot/blob/master/docs/reactcheck-2.png)
