
class SentimentVector():

    def _init_(self, position, subjectivity, polarity, anger, disgust, fear, happiness, sadness, surprise):

        self.characterisation = {"position": position, "polarity": polarity, "subjectivity": subjectivity}

        anger = (anger-1)/4
        disgust = (disgust-1)/4
        fear = (fear-1)/4
        happiness = (happiness-1)/4
        sadness = (sadness-1)/4
        surprise = (surprise-1)/4

        self.emotion = {"anger": anger, \
                            "disgust": disgust, \
                            "fear": fear, \
                            "happiness": happiness, \
                            "sadness": sadness, \
                            "surprise": surprise}
