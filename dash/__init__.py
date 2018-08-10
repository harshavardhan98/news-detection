from flask import Flask, json, request, render_template, jsonify
from flask_twitter_oembedder import TwitterOEmbedder
from random import shuffle
from flask_cache import Cache
import tweepy
import time
import atexit
from datetime import datetime
from bs4 import BeautifulSoup
from bs4.element import Comment
import urllib.request
import re
import os


from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger


from watson_developer_cloud import NaturalLanguageUnderstandingV1
from watson_developer_cloud.natural_language_understanding_v1 \
  import Features, EntitiesOptions, KeywordsOptions


natural_language_understanding = NaturalLanguageUnderstandingV1(
  username='734e8bd1-6584-4e84-b09a-4481a4346001',
  password='YCucKqbTfGCG',
  version='2018-03-16')

{
  "url": "https://gateway.watsonplatform.net/natural-language-understanding/api",
  "username": "734e8bd1-6584-4e84-b09a-4481a4346001",
  "password": "YCucKqbTfGCG"
}


app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

auth = tweepy.OAuthHandler(app.config['TWITTER_CONSUMER_KEY'],
                           app.config['TWITTER_CONSUMER_SECRET'])
auth.set_access_token(app.config['TWITTER_ACCESS_TOKEN'],
                      app.config['TWITTER_ACCESS_TOKEN_SECRET'])
tweepy_api = tweepy.API(auth)

cache = Cache(app,config={'CACHE_TYPE': 'simple'})
tweetEmbedder = TwitterOEmbedder(app,cache,100)


# accounts = ["HRDMinistry","PMOindia","FinMinIndia","HMOIndia"
# ,"ReutersTech","TechCrunch","Variety","THR","DEADLINE"]

accuonts = ["IndiaToday", "TimesNow", "ndtv", "htTweets", "CNNnews18", "timesofindia", "the_hindu", "abpnewstv", "IndianExpress", "ZeeNews", "aajtak", "DDNewsLive"]
# accounts=["DDNewsLive","IndiaToday"]

currentlyDisplayed = 0
# THIS PART HANDLES THE DB CONFIGURATION
class Tweet(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	tweetID = db.Column(db.Integer, index=True, unique=True)
	time = db.Column(db.DateTime(timezone=False), index=True, default = datetime.utcnow)
	
	def __repr__(self):
		return '<Tweet ID {} Time {}>'.format(self.tweetID,self.time)    

class Trending(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	hashtag = db.Column(db.String, index=True, unique=True)
	time = db.Column(db.DateTime(timezone=False), index=True, default = datetime.utcnow)
	


def getTweets(username):
	print("Getting From {}".format(username))
	tweets = tweepy_api.user_timeline(screen_name = username, count=4)
	# for t in tweets:
	# 	returnList.append({"tweet":t.text,
	# 						"created_at":t.created_at,
	# 						"username":username,
	# 						"headshot_url":t.user.profile_image_url
	# 					})
	print(len(tweets))
	for tweet in tweets:
		t = Tweet(tweetID=tweet.id)
		if (Tweet.query.filter_by(tweetID = tweet.id).first() is None):
			db.session.add(t)
			print("Accepted {}".format(tweet.id))

	db.session.commit()

def pull():
	print("Pulling Tweets...")
	for account in accounts:
		getTweets(account)
	
	
def readTweets():
	print("Reading Tweets from DB")
	global currentlyDisplayed
	tweets = []
	for t in db.session.query(Tweet.tweetID).order_by(Tweet.time.desc())[currentlyDisplayed:currentlyDisplayed+5]:
		tweets.append(t[0])
		# print(t[0])
	shuffle(tweets)
	currentlyDisplayed+=5
	return tweets



def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def text_from_html(url):
    html = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(html, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    para = u" ".join(t.strip() for t in visible_texts)
    para = para.split()
    hashtag = set()
    for word in para:
        if word[0] == "#":
            hashtag.add(word)
    return hashtag


def pullTrending():
	hashtagList = text_from_html("https://trends24.in/india/")
	for hashtag in hashtagList:
		t = Trending(hashtag=hashtag)
		if (Trending.query.filter_by(hashtag=hashtag).first() is None):
			db.session.add(t)
			print("Accepted {}".format(hashtag))
	db.session.commit()		

def getTrending():
	trends = []
	for t in db.session.query(Trending.hashtag).order_by(Trending.time.desc()):
		trends.append(t[0])
		# print(t[0])
	return trends	



scheduler = BackgroundScheduler()
scheduler.start()
scheduler.add_job(
    func=pull,
    trigger=IntervalTrigger(minutes=60),
    id='pullTweets',
    name='Pull Tweets every 10 minutes',
    replace_existing=True)
# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())


# https://twitter.com/search?q=%23CBSEPaperLeakExpose&src=tyah


@app.route('/')
def index():
	# pull()
	tweets = readTweets()
	# pullTrending()
	trending = getTrending()
	trendings = []
	for i in trending:
		trendings.append((i,"https://twitter.com/search?q=%23{}&src=tyah".format(i[1:])))

	print(tweets)
	return render_template("page.html",tweets=tweets,trending = trendings)

@app.route('/update',methods = ["POST"])
def update():
	print("UPDATE CALLED")
	pull()
	tweets = readTweets()
	return jsonify({'data': render_template('update.html', tweets=tweets)})

@app.route('/loadMore',methods = ["POST"])
def loadMore():
	print("LM CALLED")
	tweets = readTweets()
	return jsonify({'data': render_template('update.html', tweets=tweets)})

	