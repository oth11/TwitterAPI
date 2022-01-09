# get tweets from user, with text file containing user ids
# loop through all tweets between two dates
# output to json including all data, csv with meta data per user and csv holding all tweets

import pandas as pd
import requests
import sys
import json
import csv
import datetime

#set path variables, use two directories for easier data manipulation and extraction
tdir = "YOUROWNDIRECTORY/"    #set tweets directory
mdir = "YOUROWNDIRECTORY/"    #set meta directory

# Get user IDs from list (text file, one ID per line)
def get_usernames():
  with open('LISTFILE', 'r') as targets_file:   #textfile holding the twitter ids to check
     targets_list = targets_file.readlines()
  usernames = [] 
  for item in targets_list:
    usernames.append(item.strip('\n'))
  print("Check correct list: " + str(usernames))
  return usernames
  

# Set your BEARER Token (from Twitter API 2.0)
def auth():
    bearer_token = "TOKEN"
    # return os.environ.get('BEARER_TOKEN')
    return bearer_token


# get date - used to write filenames
now = datetime.datetime.now()
date_string = str(now.date())
print(date_string)          #screen output of date

# Create header for Twitter API with BEARER Token
def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    #print headers
    return headers


# create the needed Twitter API URLs with parameters (can be adjusted, check Twitter API documentation)
def create_url(item,last_id):
    userid = item
    
    # last_id is used to call more than 100 tweets in loops

    # Tweet fields are adjustable. We are only interested in:
    # author, tweet id, metrics, date created
    #
    # Some options:
    # attachments, context_annotations,
    # conversation_id, entities, geo, id,
    # in_reply_to_user_id, lang, non_public_metrics, organic_metrics,
    # possibly_sensitive, promoted_metrics, referenced_tweets,
    # source, and withheld

    tf = "tweet.fields=id,text,created_at,author_id,public_metrics"   # set options according to Twitter API for calling author tweets
    tf_ext = "tweet.fields=id,text,created_at,author_id,public_metrics,conversation_id,in_reply_to_user_id,referenced_tweets"
    uf = "user.fields=id,name,public_metrics"                         # set options according to Twitter API for calling author meta data
    ef = "expansions=author_id"                                       # needed to get meta data from tweets
    mr = "max_results=100"                                            # set max number of tweets per call (max. allowed = 100)
    st = "start_time=2021-01-01T00:00:00Z"                            # set start time for calling author meta data (oldest tweet)
    et = "end_time=2021-12-31T23:59:59Z"                              # set end time for calling author meta data (newest tweet)
    # ex = "exclude=retweets,replies"                                 # what to exclude: params can be retweets, replies. Adjust as needed.
    ex = ""                                                           # include all retweets, replies. Adjust as needed.
    
    if last_id == "":
      if ex == "":
        url = "https://api.twitter.com/2/users/{}/tweets?{}&{}&{}&{}&{}".format(userid, tf_ext, ef, mr, st, et)
      else:
        url = "https://api.twitter.com/2/users/{}/tweets?{}&{}&{}&{}&{}&{}".format(userid, tf, ef, mr, st, et, ex)
    else:
      if ex == "":
        url = "https://api.twitter.com/2/users/{}/tweets?until_id={}&{}&{}&{}&{}&{}".format(userid, last_id, tf_ext, ef, mr, st, et)
      else:
        url = "https://api.twitter.com/2/users/{}/tweets?until_id={}&{}&{}&{}&{}&{}&{}".format(userid, last_id, tf, ef, mr, st, et, ex)
    print(url)
    
    url_meta = "https://api.twitter.com/2/users/{}?{}".format(userid, uf)
    
    return url, url_meta  # return the URLs
    
def get_the_tweets(item):
  # Empty lists to hold all tweets and all meta data
  alltweets = []
  tweets_meta = []
  
  last_id = ""    # first call of tweets this needs to be empty (unless you want to start with older tweets)
  i = 0           # Counting the loops
  
  # get all parameters
  url, url_meta = create_url(item,last_id)
  bearer_token = auth()
  headers = create_headers(bearer_token)
  
  # get all new tweets (max. number is the first 100 tweets with the set poarameters)
  new_tweets = connect_to_endpoint(url, headers)

  # make results pretty
  nt, trash = make_json_output(new_tweets['data'])        # 2nd value (trash) not needed from this function
  mt, trash = make_json_output(new_tweets['meta'])        # 2nd value (trash) not needed from this function
  inc, trash = make_json_output(new_tweets['includes'])   # 2nd value (trash) not needed from this function
  
  # get the last tweets id called, the next token id and the no. of tweets
  last_id = json.loads(mt).get('oldest_id')
  result_count = json.loads(mt).get('result_count')
  token = json.loads(mt).get('next_token')
  ttl = result_count
  
  alltweets.append(new_tweets['data'])
  tweets_meta = new_tweets['meta']
  tweets_inc = new_tweets['includes']
  
  mfjson, mfjson_meta, mfjson_tweets_meta, mftxt, mfcsv, mfcsv_meta, mfcsv_tweets_meta, name_only = export_files(item)
  ugly, pretty = make_json_output(new_tweets['data'])
  print_routine_json((name_only + "-" + str(i) + ".json"), pretty)

  # Now get all tweets > 100 in loops, as long as there are tweets left (beware of your API limits!)
  while result_count > 0 and result_count == 100:
    i = i + 1
    # get URLs to be used
    url, url_meta = create_url(item,last_id)
    # get all new tweets (max. number is 100 tweets with the set poarameters)
    new_tweets = connect_to_endpoint(url, headers)
    
    # make results pretty
    nt, trash = make_json_output(new_tweets['data'])        # 2nd value (trash) not needed from this function
    mt, trash = make_json_output(new_tweets['meta'])        # 2nd value (trash) not needed from this function
    inc, trash = make_json_output(new_tweets['includes'])   # 2nd value (trash) not needed from this function

    # get the last tweets id called, the next token id and the no. of tweets
    last_id = json.loads(mt).get('oldest_id')
    result_count = json.loads(mt).get('result_count')
    token = json.loads(mt).get('next_token')
  
    mfjson, mfjson_meta, mfjson_tweets_meta, mftxt, mfcsv, mfcsv_meta, mfcsv_tweets_meta, name_only = export_files(item)
    ugly, pretty = make_json_output(new_tweets['data'])
    print_routine_json((name_only + "-" + str(i) + ".json"), pretty)
    
    alltweets.append(new_tweets['data'])
    tweets_meta = new_tweets['meta']
    tweets_inc = new_tweets['includes']

    ttl = ttl + result_count

  return alltweets, tweets_meta, tweets_inc

# create the outputfilenames (json and csv)
def export_files(item):
    mfjson = "{}{}-{}.json".format(tdir,date_string,item)
    mfjson_meta = "{}{}-{}_meta.json".format(mdir,date_string,item)
    mfjson_tweets_meta = "{}{}-{}_tweets_meta.json".format(mdir,date_string,item)
    mftxt = "{}{}-{}.txt".format(tdir,date_string,item)
    mfcsv = "{}{}-{}.csv".format(tdir,date_string,item)
    mfcsv_meta = "{}{}-{}_meta.csv".format(mdir,date_string,item)
    mfcsv_tweets_meta = "{}{}-{}_tweets_meta.csv".format(mdir,date_string,item)
    name_only = "{}{}-{}".format(tdir,date_string,item)
    return mfjson, mfjson_meta, mfjson_tweets_meta, mftxt, mfcsv, mfcsv_meta, mfcsv_tweets_meta, name_only

# Get tweets and meta data
def connect_to_endpoint(url, headers):
    response = requests.request("GET", url, headers=headers)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()

# Create ugly and pretty JSON outputs
def make_json_output(input):
    u = json.dumps(input)
    p = json.dumps(input, indent=4, sort_keys=True)
    return u, p

# Output data to JSON
def print_routine_json(filename,input):
  with open(filename, 'w') as f:
    f.write(str(input))
    f.close()
    # print(input)


# Call all functions and write to files
def main():
  usernames = get_usernames()
  for idx, item in enumerate(usernames):

    # write tweet data to json and csv
    mfjson, mfjson_meta, mfjson_tweets_meta, mftxt, mfcsv, mfcsv_meta, mfcsv_tweets_meta, name_only = export_files(item)
    
    # get all tweets data through API
    alltweets, tweets_meta, tweets_inc = get_the_tweets(item)
    # json_response = connect_to_endpoint(url, headers) <-- old call!

    # get all user meta data through API
    bearer_token = auth()
    url, url_meta = create_url(item,"")
    headers = create_headers(bearer_token)
    json_response_meta = connect_to_endpoint(url_meta, headers)

    ugly_meta, pretty_meta = make_json_output(json_response_meta)

    # write JSON files
    print_routine_json(mfjson_meta, pretty_meta)

if __name__ == "__main__":
    main()

