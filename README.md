twitter-backup
==============

Some python scripts to create a personal backup of Twitter Posts, Replies and DMs.  The data is stored in JSON format.

It can download the user-timeline of any public account.  For downloading the Tweets of a private account, public replies or Direct Messages, a **Twitter API key** with read/write-permissions is needed.

Obtain a Twitter API key
------------------------

Log in with your Twitter data at https://dev.twitter.com and unfold the menu under your username in the upper right corner.  Click on *My Applications* and then on *Create a new application*.

After successful creation of an API key, choose *Settings* and change it to *Read, Write and Access direct messages*.  Now it is possible to store DMs as well.

Finally an *Access Token* is needed.  This one can be created on the *Details* tab.

Installation
------------

The script is written for Python 2.7 and requires the **python-twitter wrapper** for API access.  It uses some new Twitter user-timeline API options, which are not included in the original python-twitter wrapper yet.  Use my forked version from https://github.com/larsweiler/python-twitter

Usage
-----

Whitout any option, some usage information is displayed:

	usage: twitter-backup.py [-h] [-v] [-t [username]] [-r] [-m] [-f] [-n tweets]
	                         [-o file] [--consumer_key key]
	                         [--consumer_secret secret] [--access_token_key key]
	                         [--access_token_secret secret]
	
	Create a personal backup of your Twitter Timeline replies and direct messages.
	
	optional arguments:
	  -h, --help            show this help message and exit
	  -v, --verbose         Verbose output
	  -t [username], --timeline [username]
	                        Store timeline of given username (maximum of 3200
	                        tweets)
	  -r, --replies         Store replies
	  -m, --messages        Store direct messages
	  -f, --favs            Store Favorites
	  -n tweets, --number tweets
	                        Number of Tweets to store (maximum 3200) [default:
	                        100]
	  -o file, --out file   File to store data in, otherwise use something with
	                        username and current timestamp
	  --consumer_key key    Consumer Key
	  --consumer_secret secret
	                        Consumer Secret
	  --access_token_key key
	                        Access Token Key
	  --access_token_secret secret
	                        Access Token Secret
	Specify at least one action (-t, -r, -m or -f)

Either **timeline** (`-t`), **replies** (`-r`), **messages** (`-m`) or **favs** (`-f`) needs to be specified.  With *timeline* an optional username can be specified, to store the Tweets of this user.  If an API key was given, but no username, the Tweets of the API key owner will be stored.

For the usage with an API-key all four parameters (`--consumer_key`, `--consumer_secret`, `--access_token_key`, `--access_token_secret`) are required.  The information can be found on the site where the API keys has been created.  There is no option yet to read this from a config file.

Example
-------

Download the timeline of user *chaosupdates*

	$ twitter-backup.py -t chaosupdates
	Writing to file 'chaosupdates_timeline_2012-12-03_202328.json'

An excerpt of the json file:

	['{"created_at": "Mon Dec 03 18:11:22 +0000 2012", "favorited": false, "id": 275663531926515712, "retweet_count": 8, "retweeted": false, "source": "web", "text": "Verschl\\u00fcsselung &amp; Anonymisierung: 6. Dezember, 18:30 Uhr, #Dresden \\u2013 #CryptoParty http://t.co/GXuIfS0s", "truncated": false, "user": {"id": 31812497}}', '{"created_at": "Mon Dec 03 14:32:44 +0000 2012", "favorited": false, "id": 275608511600263169, "retweet_count": 17, "retweeted": false, "source": "web", "text": "Eine sachliche Debatte sieht anders aus: Kollateralsch\\u00e4den und politische Dimension des Leistungsschutzrechts http://t.co/lnpv3SFU #LSR", "truncated": false, "user": {"id": 31812497}}',

Download last 1000 Tweets of API key owner:

	$ twitter-backup.py --consumer_key [consumer key] --consumer_secret [consumer secret] --access_token_key [access token key] --access_token_secret [access token secret] -t -n 1000

Download replies to the API key owner:

	$ twitter-backup.py --consumer_key [consumer key] --consumer_secret [consumer secret] --access_token_key [access token key] --access_token_secret [access token secret] -r

Download direct messages to and from the API key owner:

	$ twitter-backup.py --consumer_key [consumer key] --consumer_secret [consumer secret] --access_token_key [access token key] --access_token_secret [access token secret] -m

Download favorites the API key owner made:

	$ twitter-backup.py --consumer_key [consumer key] --consumer_secret [consumer secret] --access_token_key [access token key] --access_token_secret [access token secret] -f

The options can be combined, so that multiple files will be written.
