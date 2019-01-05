# Imports
from Schema import *
from Twitter import *
from Logger import *
from SentimentVector import *

from sqlalchemy import *
from sqlalchemy.orm import sessionmaker

from datetime import datetime
from pytz import timezone
import json
import unicodedata
import re
from greek_stemmer import GreekStemmer


class Pilgrim:

    def __init__(self, stdout, engine):
        self.stdout = stdout
        self.logger = Logger(self.stdout)
        self.engine = engine

    def open_session(self):
        self.logger.log_system("Connecting to database...")
        self.session = sessionmaker(bind=self.engine, autoflush=False)()
        self.logger.log_system("Connected to database.")
        return self.session

    def close_session(self):
        self.session.close()

    def extract(self, user, consumer_key, consumer_secret, access_token, access_token_secret, test):
        self.logger.init_tweet_log(user)
        self.logger.log_system("Connecting to Twitter...")
        twitter = Twitter(consumer_key, consumer_secret, access_token, access_token_secret, test)
        twitter.auth()
        self.logger.log_system("Connected. Extracting user timeline...")
        timeline = twitter.timeline(user)
        count = 0
        for tweet in timeline:
            if "text" in tweet:
                count = count + 1
                self.logger.log_system("Tweet logged: #:%d | ID:%s" % (count, tweet["id"]))
                # print json.dumps(tweet, ensure_ascii=False).encode('utf8')
                self.logger.log_tweet(tweet)
                if count >= 3180 and test:
                    self.logger.log_system("Approaching 3200 tweet limit for open API; closing connection")
                    twitter.close()
                    break
            elif "message" in tweet:
                self.logger.log_system("Message %s" % tweet[message])
                break
        self.logger.close_tweet_log()
        return self.logger.get_output_file()

    def structure(self, screen_name):
        stemmer = GreekStemmer()
        greece = timezone("Europe/Athens")
        gmt = timezone("GMT")
        self.logger.log_system("Opening extracted tweet file")
        output_file_name = "./output/tweets/%s.json" % screen_name
        output_file = open(output_file_name, "r")
        self.logger.log_system("File opened")
        user = self.session.query(User).filter_by(id=screen_name).first()
        if user is None:
            user = User(id=screen_name)
            self.session.add(user)
            self.session.commit()
        count = 0
        self.logger.log_system("Structuring tweets into database")
        for line in output_file:
            count = count + 1
            tweet = json.loads(line)
            tweet_id = tweet["id"]
            if self.session.query(Tweet).filter_by(id=tweet_id).first() is None:
                # key tweet data upload
                self.logger.log_system("Structuring tweet #:%d | id:%s | user:%s" % (count, tweet["id"], screen_name))
                is_retweet = True if "retweeted_status" in tweet else False
                is_quote = True if "quoted_status" in tweet else False
                tweet_text = tweet["text"]
                timestamp = datetime.strptime(tweet['created_at'],'%a %b %d %H:%M:%S +0000 %Y')
                timestamp = gmt.localize(timestamp)
                self.session.add(Tweet(id=tweet_id, \
                                user_id=screen_name, \
                                time_created=timestamp.strftime("%Y-%m-%d %H:%M:%S"), \
                                full_text=tweet_text, \
                                is_retweet=is_retweet, \
                                is_quote=is_quote, \
                                source=tweet["source"], \
                                in_reply_to_screen_name=tweet["in_reply_to_screen_name"]))

                # time conversion to Athens and time segmentation
                timestamp = timestamp.astimezone(greece)
                self.logger.log_system("Time segmenting tweets")
                self.session.add(TweetAnalytics(id = tweet_id, \
                                time_mapped=timestamp.strftime("%Y-%m-%d %H:%M:%S"), \
                                year_mapped=timestamp.strftime("%Y"), \
                                month_mapped=timestamp.strftime("%m"), \
                                day_mapped=timestamp.strftime("%d"), \
                                hour_mapped=timestamp.strftime("%H"), \
                                weekday_mapped=timestamp.strftime("%w"), \
                                time_segment="%s%s" % (timestamp.strftime("%Y")[-2:], timestamp.strftime("%m%d%H"))))

                # generate tokens
                self.logger.log_system("Generating tokens")
                tweet_text = re.sub(r"http\S+", "", tweet_text)             # remove links
                tweet_text = tweet_text.replace("RT @", "@")                # remove quotes
                tweet_text = tweet_text.replace('"', " ")                   # remove quotes
                tweet_text = tweet_text.replace(u"\u201D", " ")             # remove quotes
                tweet_text = tweet_text.replace(u"\u201C", " ")             # remove quotes
                tweet_text = tweet_text.replace(u"\u0387", " ")             # remove non-sentimental punctuation marks
                tweet_text = tweet_text.replace(",", " ")                   # remove non-sentimental punctuation marks
                tweet_text = tweet_text.replace(":", " ")                   # remove non-sentimental punctuation marks
                tweet_text = tweet_text.replace(".", " ")                   # remove non-sentimental punctuation marks
                tweet_text = tweet_text.replace("-", " - ")                 # pad non-sentimental punctuation marks that may be useful in context
                tweet_text = tweet_text.replace("!", " ! ")                 # pad contextual punctuation marks for parsing
                tweet_text = tweet_text.replace("?", " ? ")                 # pad contextual punctuation marks for parsing
                tweet_text = tweet_text.replace(";", " ; ")                 # pad contextual punctuation marks for parsing
                tweet_text = ' '.join(tweet_text.split())                   # remove redundant spaces
                raw_tokens = tweet_text.split()
                raw_token_count = 0
                for raw_token in raw_tokens:
                    raw_token_count = raw_token_count + 1
                    token = raw_token
                    token = ''.join(c for c in unicodedata.normalize('NFD', raw_token) if unicodedata.category(c) != 'Mn')  # remove accents
                    token = token.upper()                                                                                   # all to uppercase
                    token = stemmer.stem(token)                                                                             # get the stem
                    dictionary_token_id = ""
                    dictionary_token = self.session.query(DictionaryToken).filter_by(token=token).first()                   # look up the stem in the sentiment dictionary; bit of a rushed approach, could be done much better
                    if dictionary_token is None:
                        dictionary_token_id = None
                    else:
                        dictionary_token_id = dictionary_token.id
                    self.session.add(TweetToken(tweet_id=tweet_id, sequence=raw_token_count, token=token, raw_token=raw_token, dictionary_token=dictionary_token_id))
                self.logger.log_system("Tweet processed")
                self.session.commit()
            else:
                self.logger.log_system("Already structured tweet #:%d | id:%s " % (count, tweet["id"]))
        return output_file

    def getUserTweets(self, user):
        self.logger.log_system("Loading all tweets for user:%s" % user)
        tweets = self.session.query(Tweet).filter_by(user_id=user)
        self.logger.log_system("Tweets loaded")
        return tweets

    def analyse(self, analysis_filters, tweets):
        for filter in analysis_filters:
            filter.run(self.session, self.logger, tweets)

    def close(self):
        self.close_session()
        self.logger.close()
