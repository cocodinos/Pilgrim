
import json
import time

class Logger:
    """Simple class abstracting logs"""

    def __init__(self, stdout):
        self.system_log = open("./output/logs/system.txt", "w")
        self.stdout = stdout
        self.output_file = None
        self.log_system("Pilgrim started")

    def init_tweet_log(self, user):
        self.output_file = open("./output/tweets/%s.json" % user, "w")

    def init_analysis_output(self, filter, filename):
        self.output_file = open("./output/analysis/%s/%s.csv" % (filter, filename), "w")

    def log_analysis(self, csv_row):
        self.output_file.write(csv_row + "\n")
        if self.stdout:
            print csv_row

    def close_analysis_output(self):
        self.output_file.close()
        self.output_file = None

    def get_output_file(self):
        self.close_analysis_output()
        output = self.output_file
        self.output_file = None
        return output

    def log_tweet(self, tweet):
        string_output = json.dumps(tweet, ensure_ascii=False).encode('utf8') + "\n"
        self.output_file.write(string_output)
        if self.stdout:
            print string_output

    def close_tweet_log(self):
        self.output_file.close()

    def log_system(self, string_output):
        timestamp = time.asctime(time.gmtime(time.time()))
        string_output = "%s -- %s \n" % (timestamp, string_output)
        self.system_log.write(string_output)
        print string_output

    def close(self):
        self.log_system("Pilgrim closed")
        self.system_log.close()
