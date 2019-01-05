from Pilgrim import *
from datetime import datetime, timedelta

# some inheritance here would be nice

class FilterUserSimpleWordCount():

    def __init__(self, output_filename):
        self.output_filename = output_filename

    def run(self, session, logger, tweets):
        logger.log_system("Starting word frequency analysis")
        dictionary = dict()
        start_time = None
        end_time = None
        token_count = 0
        for tweet in tweets:
            analytics = tweet.analytics.first()
            if start_time or end_time is None:
                start_time = analytics.time_mapped
                end_time = analytics.time_mapped
            else:
                if analytics.time_mapped < start_time: start_time = analytics.time_mapped
                if analytics.time_mapped > end_time: end_time = analytics.time_mapped
            for token in tweet.tokens:
                if token.token not in dictionary: dictionary[token.token] = 0
                dictionary[token.token] += 1
                token_count += 1
        logger.log_system("Writing output")
        logger.init_analysis_output("word_count", self.output_filename)
        for key, value in sorted(dictionary.iteritems(), key=lambda (k,v): (-v,k)):
            logger.log_analysis("%s,%s,%s,%s,%s,%s" % (self.output_filename, \
                                                            start_time.strftime("%Y-%m-%d %H:%M:%S"), \
                                                            end_time.strftime("%Y-%m-%d %H:%M:%S %Z"), \
                                                            token_count, \
                                                            key.encode('utf-8'), value))
        return logger.get_output_file()

class FilterUserTweetRateAnalysis():
    def __init__(self, output_filename):
        self.output_filename = output_filename

    def run(self, session, logger, tweets):
        logger.log_system("Starting tweet rate analysis")
        timeline = dict()
        # gather the user tweets
        for tweet in tweets:
            analytics = tweet.analytics.first()
            if analytics.time_segment not in timeline:
                timeline[analytics.time_segment] = self.generate_empty_timeslot(analytics.year_mapped, \
                                                                                    analytics.month_mapped, \
                                                                                    analytics.day_mapped, \
                                                                                    analytics.hour_mapped, \
                                                                                    analytics.weekday_mapped)
            timeline[analytics.time_segment]["count"] += 1
        # add rows for time slots with user inactivity
        sorted_keys = sorted(timeline.keys())
        start_time = datetime.strptime(sorted_keys[0], '%y%m%d%H')
        end_time = datetime.strptime(sorted_keys[-1], '%y%m%d%H')
        this_time = start_time
        while this_time < end_time:
            this_time_id = datetime.strftime(this_time, '%y%m%d%H')
            if str(this_time_id) not in timeline:
                timeline[this_time_id] = self.generate_empty_timeslot(str(this_time.year), \
                                                                        str(this_time.month),
                                                                        str(this_time.day),
                                                                        str(this_time.hour),
                                                                        str(this_time.weekday()))
            this_time = this_time + timedelta(hours=1)

        # output a nice sorted timeline
        logger.log_system("Writing output")
        logger.init_analysis_output("tweet_rate", self.output_filename)
        for this_time_id in sorted(timeline.keys()):
            logger.log_analysis("%s,%s,%s,%s,%s,%s,%s,%d" % (self.output_filename.encode('utf-8'), \
                                                            this_time_id.encode('utf-8'), \
                                                            timeline[this_time_id]["weekday"].encode('utf-8'), \
                                                            timeline[this_time_id]["year"].encode('utf-8'), \
                                                            timeline[this_time_id]["month"].encode('utf-8'), \
                                                            timeline[this_time_id]["day"].encode('utf-8'), \
                                                            timeline[this_time_id]["hour"].encode('utf-8'), \
                                                            timeline[this_time_id]["count"]))
        return logger.get_output_file()

    def generate_empty_timeslot(self, year, month, day, hour, weekday):
        return {"year": year, \
                    "month": month, \
                    "day": day, \
                    "hour": hour, \
                    "weekday": weekday, \
                    "count": 0}
