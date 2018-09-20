import re
# NLTK Stop words
from nltk.corpus import stopwords
# NLTK tokenize
from nltk.tokenize import word_tokenize
# NLTK stemming
from nltk.stem import PorterStemmer


class TextProcessing(object):

    def queryProcessing(self, text):
        newText = text.lower()
        newText = re.sub('[0-9]', '', newText)
        newText = re.sub('[^ a-zA-Z0-9]', '', newText)
        # print(newText)

        # tokenize
        word_tokens = word_tokenize(newText)

        # load stop words
        stop_words = stopwords.words('english')
        # print(stop_words)

        # Remove stop words
        filterWords = [word for word in word_tokens if word not in stop_words]
        # print(filterWords)

        # stemming words
        ps = PorterStemmer()
        stemWords = []

        for word in filterWords:
            stemWords.append(ps.stem(word))
        # print(stemWords)
        return stemWords


    def resultProcessin(self, result):
        hits = result.get('hits')
        total = hits.get('total')
        print(total)
        if total >= 1:
            results = hits.get('hits')
            for entity in results:
                print(entity)


        else:
            print("Aucun resultat")