# Setup

First clone this repo and move into the directory:

```
git clone https://github.com/scottjlee/fidobot.git
cd fidobot
```

Then, install necessary packages with `pip install -r requirements.txt` (we recommend making a virtualenv).

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


### OK
In `config.json`, you should put the link to your **Admin OK panel** as the value of the `ok_link` key (e.g. https://okpy.org/admin/course/###/).

### Slack
You will need to set up Fido as a new App on your Slack workspace. 

1) Go to the [Slack App page](https://api.slack.com/apps) and create a new App. Give it a name (whatever you want) and select your workplace.
2) On the `Basic Information` page, under `Add features and functionality`, select `Incoming webhooks`, `Bots`, and `Permissions`. Then, click "Install App to Workspace."
3) On the `Bot Users` page, you should enable "Always show my bot as online." You can also customize the name and username of Fido if you wish. Change the value of the `bot_name` key in `config.json` if you change it from the default username (`fido`).
4) On the `OAuth Tokens & Redirect URLs` page, copy the Bot User OAuth Access Token and paste this as the value of the `slack_api_token` key in `config.json`.

### Piazza
We first recommend creating a fake Piazza account specifically for Fido to use as a data ingest method. Note that this account must be enrolled in the course as a TA/Professor (so that it can see private questions). You should add the following values into `config.json`:

1) Assign `piazza_id` to the Piazza class ID: `https://piazza.com/class/<Class ID>`.
2) Assign `piazza_email` to the email used to log into the fake Piazza account. 
3) Assign `piazza_password` to the password used to log into the fake Piazza account. 

**CHECK IN:** You should now have all values in `config.json` filled (no `...`'s).
