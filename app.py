from flask import Flask, render_template, request, redirect, url_for
from joblib import load
import numpy as np
from gingerit.gingerit import GingerIt
from textblob import TextBlob
import nltk
from nltk.corpus import stopwords
import os

stop_words = stopwords.words("english")
correction = ""
model_pipeline = load("scam_finder.joblib")
result = ""
probability = ""
Gmap_key=os.environ.get('GoogleMapAPIKey')#set environment variable

def get_prediction(query):
    res = model_pipeline.predict_proba([query])
    real = res[0][0]
    scam = res[0][1]
    if real <= scam: return "Scam", str(float(round(scam,4)*100))+'%'
    return "Real",  str(float(round(real,4)*100))+'%'

app = Flask(__name__, template_folder="pages")
def word(filename, final_type): # function to tokenize text 
        tok_sent = nltk.sent_tokenize(filename)
        tok_word = []
        for s in tok_sent:
            tok_word.append(nltk.word_tokenize(s))
        final_text = []
        for w in tok_word:
            if w not in stop_words:
                final_text.append(w)
        if final_type == 'sentence':
            return tok_sent
        elif final_type == 'word':
            return final_text

def check(text):
        g = GingerIt()
        h = g.parse(text)
        return len(h['corrections'])


@app.route('/')
def home():
    return render_template('forms/Home.html')


@app.route('/', methods=['POST', 'GET'])
def get_data():
    if request.method == 'POST':
        query = request.form['search']
        mistake=check(query)
        result, probability = get_prediction(query)
        return render_template('forms/Home.html', result=result, prob = probability,mis=mistake)


if __name__ == '__main__':
    app.run(debug=True)
    
    
#verify company address
#import nlp
import pandas as pd
import googlemaps
gmaps = googlemaps.Client(key=Gmap_key)

#input an address
address= input("Enter address: ")

# Geocoding an address
geocode_result = gmaps.geocode(address)

if geocode_result == []:
    print ("This address is invalid")
else:
    geocode_result= geocode_result[0]
    if 'plus_code' in geocode_result:
        print("The Company address is valid")
    else:
        print("This address is vague, This job invite is likely a scam")
