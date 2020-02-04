# Setup

First clone this repo and move into the directory:

```
git clone https://github.com/scottjlee/fidobot.git
cd fidobot
```

Then, install necessary packages with `pip install -r requirements.txt` (we recommend making a virtualenv).

## Configuration

Next, take a look inside the `config/` directory. The majority of changes you will need to make will take place in this directory. `config.json` contains the bulk of the configurable names and parameters you can change.

### Rosters
You will need to add a student and staff roster in this directory. The **student roster** can simply be downloaded from CalCentral and dropped into the directory. You should name it `roster_student.csv` (or you can change the value of the `roster_student` key in `config.json` correspondingly).

You will need to build the **staff roster** as `config/roster_staff.csv` directory (feel free to rename similarly). We recommend that you include the following information in a Google form that you send to the entire staff to fill out so you don't need to individually gather data. You should have one row for each staff member, with the following column values:

	- Name: Full name
	- Role: Person's role on staff (e.g. Professor, Lead GSI, Tutor, etc)
	- Email Address: Email address
	- Groups: Comma-separated string representing the staff member's groups, used in groupshouts (e.g. "lead, gsi")
	- Slack IDN: Person's Slack ID number, which you can find on one's Slack profile (e.g. `UM84UR7AA`)
	- Lab Number: Section number (e.g. `115`)
	- Lab Room: Dash-separated section room (e.g. `cory-105`, `evans-b6`, `sdh-254`, etc).
	- Lab Time: Section time (e.g. `W 12-2`, `T 10-12`, `F 6-8`).

**✅ CHECK IN:** You should now have a staff and student roster, with proper names updated in `config.json`.

### OK
In `config.json`, you should put the link to your **Admin OK panel** as the value of the `ok_link` key (e.g. https://okpy.org/admin/course/###/).

### Slack
You will need to set up Fido as a new App on your Slack workspace. 

1) Go to the Slack App page and create a **new Classic App by clicking [here]( https://api.slack.com/apps?new_classic_app=1)**. Give it a name (whatever you want) and select your workplace.
2) On the `Basic Information` page, click "Install App to Workspace."
3) On the `Bot Users` page, you should enable "Always show my bot as online." You can also customize the name and username of Fido if you wish. Change the value of the `bot_name` key in `config.json` if you change it from the default username (`fido`).
4) On the `OAuth Tokens & Redirect URLs` page, copy the Bot User OAuth Access Token and paste this as the value of the `slack_api_token` key in `config.json`.

**✅ CHECK IN:** You should now have all non-Piazza related values in `config.json` filled (no `...`'s).

### Piazza
We first recommend creating a fake Piazza account specifically for Fido to use as a data ingest method. Note that this account must be enrolled in the course as a TA/Professor (so that it can see private questions). You should add the following values into `config.json`:

1) Assign `piazza_id` to the Piazza class ID: `https://piazza.com/class/<Class ID>`.
2) Assign `piazza_email` to the email used to log into the fake Piazza account. 
3) Assign `piazza_password` to the password used to log into the fake Piazza account. 

**✅ CHECK IN:** You should now have all values in `config.json` filled (no `...`'s).

Now, we will set up details about Piazza pager.

**Channel mapping** In `slackbot/plugins/piazza_pager.py`, you will need to modify the `tag_to_channel_map` dictionary. The key is a folder on Piazza, and the corresponding value is a list of Slack channel names to notify. For example, if you want to notify the `content` and `pedagogy` channels when there is an unanswered question with the tag `hw1`, you should have a mapping of `{'hw1': ['content', 'pedagogy']}`.

**Forever posts** By default, Piazza pager will only look at questions that have been posted in the last week. However, there may be some posts that you want to _always_ be notified about (e.g. a master troubleshooting thread). The `forever_post_nums` variable is a set of Piazza post numbers that will always be included in paging.

### Push your changes
Now that you've made changes to Fido to fit your course, let's try it out! In the top `fidobot` directory, you should run `run.py`: `python run.py`. If you've set up everything correctly, you should be able to add Fido to a channel and use Fido commands.

**✅ CHECK IN:** You should now have a working local version of Fido.

Once you've verified that everything works locally, you should push it as a new repo (should be private, since it contains sensitive information such as rosters and passwords).

## Hosting
We use Heroku to host Fido. 

1) Create an account if you don't already have one, then go to your [Heroku Apps](https://dashboard.heroku.com/apps) page. 
2) Click "Create new app" and fill in an appropriate app name and region. Navigate to your Fido app page.
3) Under the `Deploy` tab, select Github as the deployment method. Search for your custom Fido repo and follow directions to enable automatic deploy.
4) Under the `Resources` tab, add a new Dyno. Select the free tier (unless you have credits to spare). You should now see a `worker` dyno that runs `python run.py`, exactly as we did locally. *Note:* Heroku gives 550 free dyno hours per month, which is just not enough to last the month. If you enter your credit card, they give you an additional 450 hours which is more than enough to keep Fido up and running 24/7.
5) Enable your dyno to watch Fido go!
