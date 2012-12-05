#!/usr/bin/env python
# -*- coding: utf-8 -*-


__author__ = "Lars Weiler"
__license__ = "THE NERD-WARE LICENSE (Revision 1)"
__version__ = "1.3"
__maintainer__ = "Lars Weiler"
__email__ = "lars@konvergenzfehler.de"

'''
-----------------------------------------------------------------------------
"THE NERD-WARE LICENSE" (Revision 1):
<lars@konvergenzfehler.de> wrote this file. As long as you retain this notice
you can do whatever you want with this stuff. If we meet some day, and you
think this stuff is worth it, you can buy me a beer, mate softdrink or some
food in return.
Lars Weiler
-----------------------------------------------------------------------------
'''

import argparse
import ConfigParser
import datetime
import os
import sys
import time
import twitter

def store_file(args, username, d, filetype, result):
	if args.out:
		outfile = args.out
	else:
		outfile = '%s_%s_%s.json' % (
				username,
				filetype,
				d.strftime('%Y-%m-%d_%H%M%S'))
	print("Writing to file '%s'" % outfile)
	try:
		f = open(outfile, 'w')
		f.write(str(result))
		f.close()
	except:
		print("Could not write to file '%s'" % outfile)

	return

def api_verify(args):
	if args.consumer_key and args.consumer_secret and args.access_token_key and args.access_token_secret:
		api = twitter.Api(
				consumer_key=args.consumer_key,
				consumer_secret=args.consumer_secret,
				access_token_key=args.access_token_key,
				access_token_secret=args.access_token_secret)
	elif os.path.exists(args.config):
		cf = ConfigParser.RawConfigParser()
		cf.read(args.config)
		if args.verbose:
			print("API key from config file '%s':" % (args.config))
			print(cf.items('API'))
		api = twitter.Api(
				consumer_key=cf.get('API', 'consumer_key'),
				consumer_secret=cf.get('API', 'consumer_secret'),
				access_token_key=cf.get('API', 'access_token_key'),
				access_token_secret=cf.get('API', 'access_token_secret'))
	else:
		api = twitter.Api()

	try:
		user = api.VerifyCredentials()
	except:
		print("Can not verify Credentials (API key).")
		user = None

	return (api, user)


def timeline(args, d):
	(api, user) = api_verify(args)

	if args.timeline == 'Username not given':
		try:
			username = user.screen_name
		except:
			print("No username and no API key given.")
			sys.exit(1)
	else:
		username = args.timeline

	sleeptime = 2
	retrysleeptime = 60

	# JSON object with all fetched Tweets
	result = []
	counter = 0

	try:
		# Try to fetch one Tweet, so that the Tweet-ID can be set
		rf = api.GetUserTimeline(
				screen_name=username,
				trim_user=True,
				count=1,
				page=1,
				include_rts=1)
	except twitter.TwitterError:
		print("Check your API key")
		sys.exit(1)

	# If the Tweet could be fetched, resume fetching
	if len(rf):
		# Set the Tweet-ID of the fetched Tweet in max_id; needed for walking through pages
		max_id = int(rf[-1].id)
		if args.verbose:
			print("Startdate: %s" % (rf[-1].created_at))
		# ugly hack to start the first round
		rf.append("")
		# Now walk through pages until number of Tweets is reached or no Updates available (1 Tweet returned)
		while (counter < args.number) and (len(rf) > 1):
			if args.verbose:
				print("Next round with new max_id: %d" % (max_id))
			if (args.number - counter) > 200:
				number = 200
			else:
				number = (args.number - counter) % 200
			try:
				rf = api.GetUserTimeline(
						screen_name=username,
						trim_user=True,
						count=number,
						max_id=max_id,
						include_rts=1)
			except:
				if args.verbose:
					print("Retry with the same parameters in %d seconds" % (retrysleeptime))
				time.sleep(retrysleeptime)
				continue
			counter += len(rf)
			if args.verbose:
				print("Results: %d ; Total: %d" % (len(rf), counter))
			json = [t.AsJsonString() for t in rf]
			result.extend(json)
			# Store the new max_id for the last fetched Tweet
			max_id = int(rf[-1].id)
			if args.verbose:
				print("Last date: %s" % (rf[-1].created_at))
				print("Sleeping %d seconds (otherwise Twitter gets angry)" % (sleeptime))
			time.sleep(sleeptime)

		# Finally, store all fetched Tweets
		store_file(args, username, d, 'timeline', result)

		return

def get_pages(args, d, itemtype):
	(api, user) = api_verify(args)

	sleeptime = 2
	retrysleeptime = 60

	# JSON object with all fetched Tweets
	result = []
	counter = 0
	pages = (args.number-1)/20 + 1
	page = 1

	if args.verbose:
		print("pages to fetch: %d" % (pages))
	while page <= pages:
		if args.verbose:
			print("Fetching next 20 %s" % (itemtype))
		if itemtype == 'replies':
			try:
				rf = api.GetReplies(page=page)
			except twitter.TwitterError:
				print("Check your API key")
				sys.exit(1)
		elif itemtype == 'messages':
			try:
				rf = api.GetDirectMessages(page=page)
			except twitter.TwitterError:
				print("Check your API key")
				sys.exit(1)
		elif itemtype == 'favs':
			try:
				rf = api.GetFavorites(page=page)
			except twitter.TwitterError:
				print("Check your API key")
				sys.exit(1)
		if len(rf):
				json = [t.AsJsonString() for t in rf]
				result.extend(json)
		page += 1
		if args.verbose:
			print("Last date: %s" % (rf[-1].created_at))
			print("Sleeping %d seconds (otherwise Twitter gets angry)" % (sleeptime))
		time.sleep(sleeptime)

	store_file(args, user.screen_name, d, itemtype, result)

	return


if __name__ == "__main__":
	parser = argparse.ArgumentParser(
		description='Create a personal backup of your Twitter Timeline \
				replies and direct messages.')
	parser.add_argument('-v', '--verbose',
		action='store_true',
		help='Verbose output')
	parser.add_argument('-t', '--timeline',
		metavar='username',
		nargs='?',
		const='Username not given',
		type=str,
		help='Store timeline of given username (maximum of 3200 tweets)')
	parser.add_argument('-r', '--replies',
		action='store_true',
		help='Store replies')
	parser.add_argument('-m', '--messages',
		action='store_true',
		help='Store direct messages')
	parser.add_argument('-f', '--favs',
		action='store_true',
		help='Store Favorites')
	parser.add_argument('-n', '--number',
		metavar='tweets',
		type=int,
		default=100,
		help='Number of Tweets to store (maximum 3200)\
					[default: %(default)s]')
	parser.add_argument('-o', '--out',
		metavar='file',
		type=str,
		help='File to store data in, otherwise use\
					something with username and current timestamp')
	parser.add_argument('-c', '--config',
		metavar='file',
		type=str,
		default=os.path.expanduser('~/.twitter_backup.cfg'),
		help='Path to configfile [default: %(default)s]')
	parser.add_argument('--consumer_key',
		metavar='key',
		type=str,
		help='Consumer Key')
	parser.add_argument('--consumer_secret',
		metavar='secret',
		type=str,
		help='Consumer Secret')
	parser.add_argument('--access_token_key',
		metavar='key',
		type=str,
		help='Access Token Key')
	parser.add_argument('--access_token_secret',
		metavar='secret',
		type=str,
		help='Access Token Secret')

	args = parser.parse_args(sys.argv[1:])

	if args.verbose:
		print("Application arguments:\n%s" % str(vars(args)))

	if (len(sys.argv) == 1
			or not (args.timeline
				or args.replies
				or args.messages
				or args.favs)):
		parser.print_help()
		print("Specify at least one action (-t, -r, -m or -f)")
		sys.exit(1)

	d = datetime.datetime.today()

	if args.timeline:
		timeline(args, d)

	if args.replies:
		get_pages(args, d, 'replies')

	if args.messages:
		get_pages(args, d, 'messages')

	if args.favs:
		get_pages(args, d, 'favs')

sys.exit(1)

# vim: set ts=4 sw=4:
