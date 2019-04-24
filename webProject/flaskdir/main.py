# main.py

import pandas as pd
from flask import Blueprint, render_template, request
from . import db
from flask_login import login_required, current_user
import os

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
 
import twitter_credentials

import time 
import json
from textblob import TextBlob

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)

@main.route('/proc', methods=['POST'])
@login_required
def proc():
	text = request.form['text']
	processed_text = text.lower()
	tweetProc(processed_text)
	return render_template('proc.html', mname=processed_text)

@main.route('/result')
@login_required
def result():
    analyze_sentiment()
    return render_template('result.html')

def analyze_sentiment():
	positive = 0
	neutral = 0
	negative = 0

	tweetlist = []
	for line in open('tweets.json', 'r'):
		tweetlist.append(json.loads(line))

	for i in tweetlist: 
		analysis = TextBlob(tweetlist[i])
	        
		if analysis.sentiment.polarity > 0:
			positive+=1
		elif analysis.sentiment.polarity == 0:
			neutral+=1
		else:
			negative+=1

	total = positive+neutral+negative
#The values of total,positive,neutral and negative are then passed to the highchart as a semi-donut graph

class TwitterStreamer():
    
	def __init__(self):
		pass

	def stream_tweets(self, fetched_tweets_filename, hash_tag_list):
        # This handles Twitter authetification and the connection to Twitter Streaming API
		listener = StdOutListener(fetched_tweets_filename)
		auth = OAuthHandler(twitter_credentials.CONSUMER_KEY, twitter_credentials.CONSUMER_SECRET)
		auth.set_access_token(twitter_credentials.ACCESS_TOKEN, twitter_credentials.ACCESS_TOKEN_SECRET)
		stream = Stream(auth, listener)

        # This line filter Twitter Streams to capture data by the keywords: 
		stream.filter(track=hash_tag_list)


# # # # TWITTER STREAM LISTENER # # # #
class StdOutListener(StreamListener):
    
	def __init__(self, fetched_tweets_filename, time_limit=5):
		self.start_time = time.time()
		self.limit = time_limit
		self.fetched_tweets_filename = fetched_tweets_filename

	def on_data(self, data):
		if (time.time() - self.start_time) < self.limit:            
			try:
				print(data)
				with open(self.fetched_tweets_filename, 'a') as tf:
					json_load = json.loads(data)
					text = {'text': json_load['text']}
					tf.write(json.dumps(text))


				return True
			except BaseException as e:
				print("Error on_data %s" % str(e))
			return True
		else:
			return False  

	def on_error(self, status):
		print(status)

def tweetProc(movie):
	hash_tag_list = ['movie']
	fetched_tweets_filename = "tweets.json"

	twitter_streamer = TwitterStreamer()
	twitter_streamer.stream_tweets(fetched_tweets_filename, hash_tag_list)  

