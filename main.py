from config import *
from Pilgrim import *
from Filters import *

users = [   "_lascapigliata", "efysntakton", "MrJohnSarlis", "VKostetsos"]

# "kukabonga", "_lascapigliata", "efysntakton", "skaigr", "MrJohnSarlis"

connection_string = "mysql+mysqlconnector://%s:%s@%s/%s" % (DB_USERNAME, DB_PASSWORD, DB_ADDRESS, DB_NAME)
engine = create_engine(connection_string)
pilgrim = Pilgrim(STDOUT, engine)

for user in users:
    pilgrim.extract(user, CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET, TEST)     # fetch from API
    pilgrim.open_session()                                                                              # connect to the database; local operations commencing
    pilgrim.structure(user)                                                                           # upload into database
    filters = [FilterUserTweetRateAnalysis(user), FilterUserSimpleWordCount(user)]                      # queue up analysis filters
    tweets = pilgrim.getUserTweets(user)
    output_file = pilgrim.analyse(filters, tweets)                                                      # run each filter
pilgrim.close()
