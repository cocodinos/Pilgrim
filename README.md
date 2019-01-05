# Pilgrim

Pilgrim is a simple framework for analysis of Tweets in Greek.  Its purpose is to enable analysis for coordinated troll farm attacks.  Pilgrim uses the Twitter API (free or premium) to download tweets, structures them in a database by time segmenting and tokenising them using.  It also integrates a Greek sentiment dictionary based on the [MKLab-ITI Greek sentiment lexicon](https://github.com/MKLab-ITI/greek-sentiment-lexicon) that can be referenced using [GreekStemmer](https://pypi.org/project/greek-stemmer/)

The framework consists of

* The database schema (the approach for organising the information in preparation for analysis)
* The process for data extraction, upload
* The implementation of AnalysisFilters; contributors should be able to develop their own, which should plug in seamlessly to the framework; this way they are able to run their own analysis

It is still work in progress, i.e. non-optimised, using beginner Python, and with very little error handling; this working prototype is meant as a proof of concept.  The tool is stable enough for testing, and seems to behave well

Contributions are welcome!

## Background

The thesis of the project is that well-organised troll farms (rather than individual activists) are very active on Twitter in Greek and instrumental in controlling the narrative within that small ecosystem.  On the basis of this thesis, these troll farms should not behave like normal users.  Initial analysis on some accounts validates these findings with evidence such as unusually high volume of tweets for a single individual, abnormal focus on inflammatory keywords and regular "working hours".

Lexical analysis, signal correlations and could help reveal patterns of operation and individual account operators' "[fists](https://cromwell-intl.com/travel/uk/bletchley-park/)"

## Prerequisites

The script is in Python 2.7.  Dependencies (use pip to install) include:

* sqlalchemy
* pytz
* datetime
* re
* unicodedata
* greek-stemmer
* TwitterAPI
* requests_oauthlib
* urlparse

You will also need:

* Access to a MySQL server where you can set up a database with a username and password.  We are thinking of creating an AWS RDS instance to share data; message @psopsodinos if you are interested discuss
* Twitter API keys to download data.  Again, message @psopsodinos if you are open to sharing resources on this

## Installing

1. Set up the config.py file with your credentials for Twitter, your MySQL server and whether you want to see detailed output on STDEV
2. Run the setup.py script in order to generate the schema in your database
3. Run the SQL script DictionaryTokens.sql against your database to populate the TweetDictionary

## Using

In main.py, you can establish a list of users you want to audit, using their Twitter screen names, e.g.

```
users = ["skaigr", "psopsodinos"]
```

The script will extract their latest 3150 tweets, upload them to the database and provide you with some (for the time being) basic hooks for your analysis.  We use the Premium API to extract larger volumes of data.  

As an entry point to your analysis, you can request a handle to a user's tweets from the database with:

```
tweets = pilgrim.getUserTweets(user)
```

This returns a MySQL ORM query to the user, that you can use to navigate to the data you want and run your analysis.  Take a look at Schema.py to get a sense of the structure of the database.

Your analysis can be implemented within classes implementing a super basic Interface/ Pattern we call Filter.  An example, FilterUserSimpleWordCount, outputting to .csv for analysis in Excel, is included. The demo filter analyses the set of tweets submitted to it to calculate the frequency of words used by the Twitter account, returning word roots and frequency in descending order.  

You can run multiple filters within a batch process.

```
user = "skaigr"
filters = [FilterUserSimpleWordCount(user), FilterAnotherFilter("output filename")]                                                     
tweets = pilgrim.getUserTweets(user)
for filter in filters:
    output_file = pilgrim.analyse(filters, tweets)
```

If you already have completed parts of the extraction and structuring process, you can choose to comment out the parts of that you want to skip.  For example, this script will not extract data from the API or upload to the database and will just skip to the analysis.

```
for user in users:
    # pilgrim.extract(user, CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET, TEST)   # COMMENT OUT - NO TWITTER API QUERY
    pilgrim.open_session()                                                                          
    # pilgrim.structure(user)                                                                         # COMMENT OUT - NO UPLOAD TO DATABASE
    filters = [FilterUserSimpleWordCount(user)]                                                     
    tweets = pilgrim.getUserTweets(user)
    for filter in filters:
        output_file = pilgrim.analyse(filters, tweets)                                              
pilgrim.close()
```

Happy analysis!

## Authors

* [@psopsodinos](http://twitter.com/psopsodinos)
