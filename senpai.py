import tweepy
import json
import re
import csv

with open('./token.json') as file:
    j = json.load(file)

consumer_key = j['api_key']
consumer_secret = j['api_secret_key']
access_token = j['access_token']
access_token_secret = j['access_token_secret']

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# -------------------------------------------------------------------
TARGET_ACCOUNT = "DrunkTozan"
LAST_TWEET_FILE = "./DrunkSenpai_last.json"

# Special prefixes
# d_* : parse as datetime value
# f_* : parse as float(real) value
# i_* : parse as integer value
# no prefix: parse as string value
TWEET_PERSER = {
  'DrunkSenpai.csv': [
    r'drunk! @ (?P<d_date>\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2})',
    r'\s*(?P<f_amount_ml>\d+\.\d+)ml',
    r'today\s*(?P<f_today_ml>\d+\.\d+)ml \((?P<i_today_glasses>\d+)glasses\)',
    r'bottle\s*(?P<f_bottle_ml>\d+\.\d+)ml \((?P<i_bottle_glasses>\d+)glasses\)',
    r'total\s*(?P<f_total_ml>\d+\.\d+)ml \((?P<i_total_glasses>\d+)glasses\)',
  ],
  'DrunkSenpai_NewBottle.csv': [
    r'new bottle arrival! @ (?P<d_date>\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2})'
  ],
  'DrunkSenpai_OldFormat.csv': [ # Always system is growing. Also me too.
    r'drunk! @ (?P<d_date>\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2})',
    r'\s*(?P<f_amount_ml>\d+\.\d+)ml',
    r'today\s*(?P<f_today_ml>\d+\.\d+)ml$',
    r'total\s*(?P<f_total_ml>\d+\.\d+)ml$',
  ]
}

def parse_tweets(tweets: list) -> dict:
  parsed_tweets: dict = {}

  for tweet in tweets:
    parsed_tweet = parse_tweet(tweet, TWEET_PERSER)
    if parsed_tweet is None:
      # Todo: Output error log here. The tweet is not supported format in TWEET_PERSER.
      continue
    (file_name, row) = parsed_tweet
    if file_name not in parsed_tweets:
      parsed_tweets[file_name] = []
    parsed_tweets[file_name].insert(0, row)
  return parsed_tweets


def parse_tweet(tweet, patterns: list) -> (str, dict):
  lines = tweet.text.splitlines()
  for file_name, parttern_list in patterns.items():
    match_result = match_tweet(lines, parttern_list)
    if match_result is None:
      continue

    return (file_name, dict({'id': tweet.id}, **match_result))

  return None

def match_tweet(lines: list, pattern_list: list) -> dict:
  matches = {}
  if len(lines) != len(pattern_list):
    return None

  for line, pattern in zip(lines, pattern_list):
    pat = re.compile(pattern)
    res = pat.match(line)
    if res is None:
      return None

    matches_row = res.groupdict()

    # print(len(matches_row), pat.groups)
    if len(matches_row) != pat.groups:
      return None

    converted_row = match_convert(matches_row)
    matches.update(converted_row)

  return matches


def match_convert(matches: dict) -> dict:
    res = {}
    for k, v in matches.items():
      if k.startswith('d_'):
        res[k.replace('d_', '', 1)] = v.replace('/', '-')
        continue
      if k.startswith('f_'):
        res[k.replace('f_', '', 1)] = float(v)
        continue
      if k.startswith('i_'):
        res[k.replace('i_', '', 1)] = int(v)
        continue
      res[k] = v
    return res

try:
    with open(LAST_TWEET_FILE) as f:
        since_id = json.load(f)['id']
except:
    since_id = '1'

tweets = api.user_timeline(TARGET_ACCOUNT, count=10, page=1, since_id=since_id)
if len(tweets) <= 0:
    exit()

filename_parsedtweets = parse_tweets(tweets)
last_id = max([t.id for t in tweets])

def store_last_tweet(last_id, last_tweetd_file=LAST_TWEET_FILE):
    with open(last_tweetd_file, 'w') as file:
        file.write(json.dumps({'id': last_id}))

store_last_tweet(last_id, last_tweetd_file=LAST_TWEET_FILE)

def write_csv(drunks=[], target_csv="sample.csv", is_append=True):
    if len(drunks) <= 0:
        return

    option = 'w'
    if is_append:
        option = 'a'

    with open(target_csv, option) as f:
        writer = csv.DictWriter(f, drunks[0].keys())
        writer.writeheader()
        writer.writerows(drunks)

for file_name, parsed_tweets in filename_parsedtweets.items():
  write_csv(parsed_tweets, file_name, is_append=False)
