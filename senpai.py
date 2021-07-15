import tweepy
import json
import re
import csv


with open('./token.json') as file:
  j = json.load(file)

consumer_key = j['api_key']
consumer_secret =j['api_secret_key']
access_token = j['access_token']
access_token_secret = j['access_token_secret']

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

#-------------------------------------------------------------------
TARGET_ACCOUNT = "DrunkTozan"
LAST_TWEET_FILE = "./DrunkSenpai_last.json"
CSV_FILE_NAME = "./DrunkSenpai.csv"

try:
  with open(LAST_TWEET_FILE) as f:
    since_id = json.load(f)['id']
except:
  since_id = '1'


tweets = api.user_timeline(TARGET_ACCOUNT, count=10, page=1, since_id=since_id)

drunks = []
for tweet in tweets:
  (date_r, amount_r, today_r, total_r) = tweet.text.splitlines()
  drunk = {
    'id': tweet.id,
    'date': re.search(r'\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}', date_r).group(),
    'amount_ml': float(re.search(r'\d+\.\d+', amount_r).group()),
    'today_ml':  float(re.search(r'\d+\.\d+', amount_r).group()),
    'total': "" #  re.search(r'\d+\.\d+', total_r).group() # it seems is not implemented ?
  }
  drunks.insert(0, drunk)

if len(drunks) <= 0:
    exit()

def store_last_tweet(drunks=[], last_tweetd_file=LAST_TWEET_FILE):
  with open(last_tweetd_file, 'w') as file:
    file.write(json.dumps(drunks[-1]))
store_last_tweet(drunks, last_tweetd_file=LAST_TWEET_FILE)


def write_csv(drunks=[], target_csv=CSV_FILE_NAME, is_append=True):
  if len(drunks) <= 0:
    return

  option = 'w'
  if is_append:
    option = 'a'

  with open(target_csv, option) as f:
    writer = csv.DictWriter(f, drunks[0].keys())
    writer.writeheader()
    writer.writerows(drunks)
write_csv(drunks, CSV_FILE_NAME, is_append=False)

