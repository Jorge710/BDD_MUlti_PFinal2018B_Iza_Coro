import json
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from textblob import TextBlob
from elasticsearch import Elasticsearch

# import twitter keys and tokens
from config import *

# create instance of elasticsearch
es = Elasticsearch()

def obtenerFecha (fecha):
        listaFecha = fecha.split(' ')
        #print(listaFecha[1])
        mes = " "
        if listaFecha[1] == "Jan":
                mes = "01"
        elif listaFecha[1] == "Feb":
                mes = "02"
        elif listaFecha[1] == "Mar":
                mes = "03"
        elif listaFecha[1] == "Apr":
                mes = "04"
        elif listaFecha[1] == "May":
                mes = "05"
        elif listaFecha[1] == "Jun":
                mes = "06"
        elif listaFecha[1] == "Jul":
                mes = "07"
        elif listaFecha[1] == "Aug":
                mes = "08"
        elif listaFecha[1] == "Sep":
                mes = "09"
        elif listaFecha[1] == "Oct":
                mes = "10"
        elif listaFecha[1] == "Nov":
                mes = "11"
        else:
                mes = "12"

        año=listaFecha[5]
        mes = mes
        dia = listaFecha[2]
        nuevaFecha = año+"-"+mes+"-"+dia

        return nuevaFecha


class TweetStreamListener(StreamListener):

    # on success
    def on_data(self, data):

        lon = 0
        lat = 0

        # decode json
        dict_data = json.loads(data)

        # pass tweet into TextBlob
        tweet = TextBlob(dict_data["text"])
        try:
            fecha = dict_data["created_at"]
            print(obtenerFecha(fecha))
            formatoFecha = obtenerFecha(fecha)
            geo = dict_data["coordinates"]["coordinates"]
            print(geo)
            lon = geo[0]
            lat = geo[1]

            es.index(index="alcaldia_quito",
                 doc_type="test-type",
                 body={"author": dict_data["user"]["screen_name"],
                       "date": formatoFecha,
                       "message": dict_data["text"],
                       "location":[lon,lat],
                       "geo":dict_data["user"]["location"],
                       "polarity": tweet.sentiment.polarity,
                       "subjectivity": tweet.sentiment.subjectivity,
                       "sentiment": sentiment})
            return True
          
        
        except:
            print("No hay datos")

        # output sentiment polarity
        #print (tweet.sentiment.polarity)

        # determine if sentiment is positive, negative, or neutral
        if tweet.sentiment.polarity < 0:
            sentiment = "negative"
        elif tweet.sentiment.polarity == 0:
            sentiment = "neutral"
        else:
            sentiment = "positive"

        # output sentiment
        #print (sentiment)
	
        # add text and sentiment info to elasticsearch
        es.index(index="alcaldia_quito",
                 doc_type="test-type",
                 body={"author": dict_data["user"]["screen_name"],
                       "date": formatoFecha,
                       "message": dict_data["text"],
                       "geo":dict_data["user"]["location"],
                       "location":[lon,lat],
                       "polarity": tweet.sentiment.polarity,
                       "subjectivity": tweet.sentiment.subjectivity,
                       "sentiment": sentiment})
        return True
        

    # on failure
    def on_error(self, status):
        print (status)

if __name__ == '__main__':

    # create instance of the tweepy tweet stream listener
    listener = TweetStreamListener()

    # set twitter keys/tokens
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    # create instance of the tweepy stream
    stream = Stream(auth, listener)

    # search twitter for "Ecuador" keyword
    stream.filter(track=['LoroHomero','PacoMoncayo','CesarMontufar51','PaolaVintimilla','juancaholguin'])
    #stream.filter(locations=[-78.586922,-0.395161,-78.274155,0.021973])
