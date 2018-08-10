from bs4 import BeautifulSoup
from bs4.element import Comment
import urllib.request
import re
import tweepy
import os

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



def getTweets(hashtag):
    auth = tweepy.OAuthHandler(os.environ['TWITTER_CONSUMER_KEY'],
                           os.environ['TWITTER_CONSUMER_SECRET'])
    auth.set_access_token(os.environ['TWITTER_ACCESS_TOKEN'],
                      os.environ['TWITTER_ACCESS_TOKEN_SECRET'])
    tweepy_api = tweepy.API(auth)

    print("Pulling {}".format(hashtag))

    tweets = tweepy_api.search(q=hashtag, lang="en", count = 2)
    for tweet in tweets:
        print (tweet.text)




if __name__ == "__main__":
    getTweets(text_from_html("https://trends24.in/india/"))
    # getTweets("lol")
