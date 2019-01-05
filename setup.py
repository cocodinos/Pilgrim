
from schema import *
import csv
from greek_stemmer import GreekStemmer
import unicodedata
from sqlalchemy.orm import sessionmaker

# session = sessionmaker(bind=engine)()
# stemmer = GreekStemmer()
# for token in session.query(DictionaryToken):
#     token.token = stemmer.stem(token.token)
#     session.commit()

Base.metadata.create_all(engine)
