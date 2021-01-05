# get tweets from user, with text file containing user ids
# loop through all tweets between two dates
# output to json including all data, csv with meta data per user and csv holding all tweets

#import os
#import pandas as pd
#from pandas.io.json import json_normalize

import requests
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import json
from datetime import date
from datetime import datetime

#set path variables, use two directories for easier data manipulation and extraction
tdir = "tweets_DIR/" #set tweets directory
mdir = "meta_DIR/"   #set meta directory

# Get user IDs from list (text file, one ID per line)
def get_usernames():
  with open('list.txt', 'r') as targets_file:   # pulled from working directory
     targets_list = targets_file.readlines()
  usernames = [] 
  for item in targets_list:
    usernames.append(item.strip('\n'))
  print("Check correct list: " + str(usernames))
  return usernames
  

# Set your BEARER Token (from Twitter API 2.0)
def auth():
    bearer_token = "YOUR BEARER TOKEN"
    # return os.environ.get('BEARER_TOKEN') # in case you have set your Bearer Token in your environment
    return bearer_token


# Get current date and timestamp to use with filenames
dt = datetime.now()
call_day = dt.strftime("%Y%m%d")
timestamp = (dt - datetime(1970, 1, 1)).total_seconds()


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
    uf = "user.fields=id,name,public_metrics"                         # set options according to Twitter API for calling author meta data
    ef = "expansions=author_id"                                       # needed to get meta data from tweets
    mr = "max_results=100"                                            # set max number of tweets per call (max. allowed = 100)
    st = "start_time=2020-10-01T00:00:00Z"                            # set start time for calling author meta data (oldest tweet)
    et = "end_time=2020-12-31T23:59:59Z"                              # set end time for calling author meta data (newest tweet)
    ex = "exclude=retweets,replies"                                   # exclude all retweets and replies. Adjust as needed.

    if last_id == "":
      url = "https://api.twitter.com/2/users/{}/tweets?{}&{}&{}&{}&{}&{}".format(userid, tf, ef, mr, st, et, ex)
    else:
      url = "https://api.twitter.com/2/users/{}/tweets?until_id={}&{}&{}&{}&{}&{}&{}".format(userid, last_id, tf, ef, mr, st, et, ex)
    
    url_meta = "https://api.twitter.com/2/users/{}?{}".format(userid, uf)
    
    print "\nURLs for user id {}\nURL: {}\nMeta URL: {}".format(userid,url,url_meta)  # check your URLs
    # print url, url_meta   # check your URLs
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

  print "\n***LOOP for ***: {}".format(item)
  # make results pretty --> not really needed here. Can be used to check results :)
  nt, trash = make_json_output(new_tweets['data'])        # 2nd value (trash) not needed from this function
  mt, trash = make_json_output(new_tweets['meta'])        # 2nd value (trash) not needed from this function
  inc, trash = make_json_output(new_tweets['includes'])   # 2nd value (trash) not needed from this function
  
  # get the last tweets id called, the next token id and the no. of tweets
  last_id = json.loads(mt).get('oldest_id')
  result_count = json.loads(mt).get('result_count')
  token = json.loads(mt).get('next_token')
  ttl = result_count
  
  print "\n***OLDEST***: \nCount: {}\nToken: {}\nLast ID: {}".format(result_count, token, last_id)

  # append data to list
  alltweets.append(new_tweets['data'])
  tweets_meta = new_tweets['meta']
  tweets_inc = new_tweets['includes']
  
  # write json data
  mfjson, mfjson_meta, mfjson_tweets_meta, mftxt, mfcsv, mfcsv_meta, mfcsv_tweets_meta, name_only = export_files(item)
  ugly, pretty = make_json_output(new_tweets['data'])
  print_routine_json((name_only + "-" + str(i) + ".json"), pretty)

  # print "\n***all data***"
  # print alltweets
  # print "\n***no. of tweets***"
  # print len(new_tweets['data'])
  # tweets_meta.append(new_tweets['meta'])
  # print "\n***current meta***"
  # print tweets_meta
  # print new_tweets
  
  # Now get all tweets > 100 in loops, as long as there are tweets left (beware of your API limits!)
  while result_count > 0 and result_count == 100:
    i = i + 1
    print ("\ngetting tweets before: {}").format(last_id)
    # get URLs to be used
    url, url_meta = create_url(item,last_id)
    # get all new tweets (max. number is 100 tweets with the set poarameters)
    new_tweets = connect_to_endpoint(url, headers)
    
    print "\n***LOOP for***{}, loop no. {}".format(item,i)
    
    # make results pretty --> not really needed here. Can be used to check results :)
    nt, trash = make_json_output(new_tweets['data'])        # 2nd value (trash) not needed from this function
    mt, trash = make_json_output(new_tweets['meta'])        # 2nd value (trash) not needed from this function
    inc, trash = make_json_output(new_tweets['includes'])   # 2nd value (trash) not needed from this function

    # get the last tweets id called, the next token id and the no. of tweets
    last_id = json.loads(mt).get('oldest_id')
    result_count = json.loads(mt).get('result_count')
    token = json.loads(mt).get('next_token')
  
    print "\n***OLDEST***: \nCount: {}\nToken: {}\nLast ID: {}".format(result_count, token, last_id)

    # write json data
    mfjson, mfjson_meta, mfjson_tweets_meta, mftxt, mfcsv, mfcsv_meta, mfcsv_tweets_meta, name_only = export_files(item)
    ugly, pretty = make_json_output(new_tweets['data'])
    print_routine_json((name_only + "-" + str(i) + ".json"), pretty)

    # append data to list
    alltweets.append(new_tweets['data'])
    tweets_meta = new_tweets['meta']
    tweets_inc = new_tweets['includes']

    ttl = ttl + result_count
    print ("\n...{} tweets downloaded so far").format(ttl)

  return alltweets, tweets_meta, tweets_inc
  # print new_tweets
  
# create the outputfiles (json and csv)
def export_files(item):
    mfjson = "{}{}-{}.json".format(tdir,call_day,item)
    mfjson_meta = "{}{}-{}_meta.json".format(mdir,call_day,item)
    mfjson_tweets_meta = "{}{}-{}_tweets_meta.json".format(mdir,call_day,item)
    mftxt = "{}{}-{}.txt".format(tdir,call_day,item)
    mfcsv = "{}{}-{}.csv".format(tdir,call_day,item)
    mfcsv_meta = "{}{}-{}_meta.csv".format(mdir,call_day,item)
    mfcsv_tweets_meta = "{}{}-{}_tweets_meta.csv".format(mdir,call_day,item)
    name_only = "{}{}-{}".format(tdir,call_day,item)
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

# Normalize data and output to CSV --> not used. Throws errors. Use R scripts instead.
def print_routine_csv(filename,input):
  pd.set_option("max_columns", -1) # show all cols
  pd.set_option('max_colwidth', -1) # show full width of showing cols
  pd.set_option("expand_frame_repr", -1) # print cols side by side as it's supposed to bepd.set_option('display.max_columns', None)
  pd.set_option('display.max_colwidth', -1)
  # output = input
  print type(input), input
  # if type(input) is list:
  #   output = pd.DataFrame(input)
  #   # if type(output) is dict or type(output) is list:
  #   #   output = pd.DataFrame(output)
  #   #   pass
  #   pass
  # elif type(input) is dict:
  #   output = pd.DataFrame(input)
  #   pass
  # else:
  #   output = json_normalize(input)
  output = json.dumps(input)
  output = pd.DataFrame(output)
  print output
  output.to_csv(filename, index = False, header=True)

# Call all functions and write to files
def main():
  usernames = get_usernames()
  for idx, item in enumerate(usernames):
    print "\n*** We are in MAIN***: id= {}, user= {}".format(idx,item)

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

    # control printout - can be deleted
    print "length of alltweets: {}".format(len(alltweets))
    print "type of alltweets: {}".format(type(alltweets))
    print "length of tweets_meta: {}".format(len(tweets_meta))
    print "type of tweets_meta: {}".format(type(tweets_meta))
    print "length of tweets_inc: {}".format(len(tweets_inc))
    print "type of tweets_inc: {}".format(type(tweets_inc))
    print "length of json_response_meta: {}".format(len(json_response_meta))
    print "type of json_response_meta: {}".format(type(json_response_meta))

    # ugly, pretty = make_json_output(alltweets[0])
    # ugly, pretty = make_json_output(alltweets)
    ugly_meta, pretty_meta = make_json_output(json_response_meta)
    # ugly_tweets_meta, pretty_tweets_meta = make_json_output(tweets_meta) #list indices must be integers, not str
    
    # write JSON files from metaURL. All other data from tweets written with function get_the_tweets
    # print_routine_json(mfjson, pretty)
    print_routine_json(mfjson_meta, pretty_meta)
    # write last meta json to file. Note needed for further processing.
    # print_routine_json(mfjson_tweets_meta, pretty_tweets_meta)

    # write CSV files - done with R script
    # print_routine_csv(mfcsv, alltweets[0])
    # print_routine_csv(mfcsv_meta,json_response_meta)
    # print_routine_csv(mfcsv, ugly)
    # print_routine_csv(mfcsv_meta,ugly_tweets_meta)

  el_time = ((datetime.now() - datetime(1970, 1, 1)).total_seconds() - timestamp)
  print ("elapsed time: {} seconds").format(el_time)
  
  
if __name__ == "__main__":
    main()
