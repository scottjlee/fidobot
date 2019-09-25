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
	- Groups: Comma-separated string representing the staff member's groups (e.g. "lead, gsi")
	- Slack IDN: Person's Slack ID number, which you can find on one's Slack profile (e.g. `UM84UR7AA`)
	- Lab Number: Section number (e.g. `115`)
	- Lab Room: Dash-separated section room (e.g. `cory-105`, `evans-b6`, `sdh-254`, etc).
	- Lab Time: Section time (e.g. `W 12-2`, `T 10-12`, `F 6-8`).



