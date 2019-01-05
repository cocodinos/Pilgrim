from sqlalchemy import *
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import *

engine = create_engine("mysql+mysqlconnector://root:NuckyThompson123@localhost:3306/pilgrim")

# engine = create_engine('sqlite:///:memory:')
Base = declarative_base()

class User(Base):
    __tablename__ = 'Users'
    id = Column(String(50), primary_key=True)
    tweets = relationship("Tweet", backref="user", lazy="dynamic")

class Tweet(Base):
    __tablename__ = 'Tweets'
    id = Column(String(50), primary_key=True)
    user_id = Column(String(50), ForeignKey('Users.id'))
    time_created = Column(DateTime)
    full_text = Column(Text)
    is_retweet = Column(Boolean)
    is_quote = Column(Boolean)
    source = Column(String(100))
    in_reply_to_screen_name = Column(String(50))
    analytics = relationship("TweetAnalytics", backref="tweets", lazy="dynamic")
    tokens = relationship("TweetToken", backref="tweet", lazy="dynamic")

class TweetAnalytics(Base):
    __tablename__ = 'TweetAnalytics'
    id = Column(String(50), ForeignKey('Tweets.id'), primary_key=True)
    time_mapped = Column(DateTime)
    year_mapped = Column(String(4))
    month_mapped = Column(String(2))
    day_mapped = Column(String(2))
    hour_mapped = Column(String(2))
    weekday_mapped = Column(String(1))
    time_segment = Column(String(8))

class TweetToken(Base):
    __tablename__ = 'TweetTokens'
    sequence = Column(Integer, primary_key=True)
    tweet_id = Column(String(50), ForeignKey('Tweets.id'), primary_key=True)
    raw_token = Column(String(300))
    token = Column(String(300))
    dictionary_token = Column(Integer, ForeignKey('DictionaryTokens.id'))

class DictionaryToken(Base):
    __tablename__ = 'DictionaryTokens'
    id = Column(Integer, primary_key=True)
    token = Column(String(50))
    raw_token = Column(String(50))
    position = Column(String(8))
    subjectivity = Column(String(5))
    polarity = Column(String(5))
    anger = Column(TINYINT())
    disgust = Column(TINYINT())
    fear = Column(TINYINT())
    happiness = Column(TINYINT())
    sadness = Column(TINYINT())
    surprise = Column(TINYINT())
