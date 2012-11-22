#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import sys
import datetime
import time
import twitter

def store_file(args, d, filetype, result):
	if args.out:
		outfile = args.out
	else:
		outfile = '%s_%s_%s.json' % (
				args.user,
				filetype,
				d.strftime('%Y-%m-%d_%H%M%S'))
	if args.verbose:
		print("Writing to file '%s'" % outfile)
	try:
		f = open(outfile, 'w')
		f.write(str(result))
		f.close()
	except:
		print("Could not write to file '%s'" % outfile)

	return

def timeline(args, d):
	api = twitter.Api()

	sleeptime = 2
	retrysleeptime = 60

	result = []
	counter = 0

	rf = api.GetUserTimeline(
			screen_name=args.user,
			trim_user=True,
			count=1,
			page=1,
			include_rts=1)
	if len(rf):
		max_id = int(rf[-1].id)
		if args.verbose:
			print("Startdate: %s" % (rf[-1].created_at))
		while counter < args.number:
			print("Next round with new max_id: %d" % (max_id))
			if (args.number - counter) > 200:
				number = 200
			else:
				number = (args.number - counter) % 200
			try:
				rf = api.GetUserTimeline(
						screen_name=args.user,
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
			max_id = int(rf[-1].id)
			if args.verbose:
				print("Last date: %s" % (rf[-1].created_at))
				print("Sleeping %d seconds (otherwise Twitter gets angry)" % (sleeptime))
			time.sleep(sleeptime)

			store_file(args, d, 'timeline', result)

			return

def replies(args, d):
	api = twitter.Api(
			consumer_key=args.consumer_key,
			consumer_secret=args.consumer_secret,
			access_token_key=args.access_token_key,
			access_token_secret=args.access_token_secret)

	sleeptime = 2
	retrysleeptime = 60

	result = []
	counter = 0
	pages = (args.number-1)/20 + 1
	page = 1

	if args.verbose:
		print("pages to fetch: %d" % (pages))

	while page <= pages:
		if args.verbose:
			print("Fetching next 20 Replies")
		rf = api.GetReplies(page=page)
		if len(rf):
				json = [t.AsJsonString() for t in rf]
				result.extend(json)
		page += 1

	store_file(args, d, 'replies', result)

	return

def messages(args, d):
	api = twitter.Api(
			consumer_key=args.consumer_key,
			consumer_secret=args.consumer_secret,
			access_token_key=args.access_token_key,
			access_token_secret=args.access_token_secret)

	sleeptime = 2
	retrysleeptime = 60

	result = []
	counter = 0
	pages = (args.number-1)/20 + 1
	page = 1

	if args.verbose:
		print("pages to fetch: %d" % (pages))

	while page <= pages:
		if args.verbose:
			print("Fetching next 20 Direct Messages")
		rf = api.GetDirectMessages(page=page)
		if len(rf):
				json = [t.AsJsonString() for t in rf]
				result.extend(json)
		page += 1

	store_file(args, d, 'messages', result)

	return

if __name__ == "__main__":
	parser = argparse.ArgumentParser(
		description='Create a personal backup of your Twitter Timeline \
				replies and direct messages.')
	parser.add_argument('-v', '--verbose',
		action='store_true',
		help='Verbose output')
	parser.add_argument('-t', '--timeline',
		action='store_true',
		help='Store timeline (maximum of 3200 tweets)')
	parser.add_argument('-r', '--replies',
		action='store_true',
		help='Store replies')
	parser.add_argument('-m', '--messages',
		action='store_true',
		help='Store direct messages')
	parser.add_argument('-n,', '--number',
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
	parser.add_argument('user',
		metavar='user',
		type=str,
		help='The user to backup')

	if len(sys.argv) == 1:
		parser.print_help()
		print("No Username given")
		sys.exit(1)

	args = parser.parse_args(sys.argv[1:])

	if args.verbose:
		print("Application arguments:\n%s" % str(vars(args)))

	if not args.timeline and not args.replies and not args.messages:
		print("Specify either timeline or replies")
		sys.exit(1)

	d = datetime.datetime.today()

	if args.timeline:
		timeline(args, d)

	if args.replies:
		replies(args, d)

	if args.messages:
		messages(args, d)

sys.exit(1)

# vim: set ts=4 sw=4:
