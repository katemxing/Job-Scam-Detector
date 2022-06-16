from flask import Flask, render_template, request
from joblib import load
from gingerit.gingerit import GingerIt
import nltk
from nltk.corpus import stopwords
import os
import googlemaps
import pysbd


stop_words = stopwords.words("english")
correction = ""
model_pipeline = load("scam_finder.joblib")
result = ""
probability = ""
apikey=os.environ.get('GoogleMapAPIKey')#retrieve environment variable



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

#verify company address
def get_map_info(address):
    gmaps = googlemaps.Client(key=apikey)
    geocode_result = gmaps.geocode(address)
    if geocode_result == []:
        output="This address is invalid"
    else:
        geocode_result= geocode_result[0]
        if 'plus_code' in geocode_result:
            output="The Company address is valid"
        else:
            output="This address is vague, This job invite is likely a scam"
    return output #return desinated string content


@app.route('/')
def home():
    return render_template('forms/Home.html')


@app.route('/', methods=['POST', 'GET'])
def get_data():
    if request.method == 'POST':
        #segment the input text by '.', transfer the output list back to string
        rawtext = request.form['text']
        seg = pysbd.Segmenter(language='en', clean=False) #define segmenter
        textlist = seg.segment(rawtext)
        for i in (0,len(textlist)-1):
            text = textlist[i]
        mistake=check(text)
        #request for address variable if user inputs, otherwise use output as null
        try:
            addr = request.form['addr']
            address=get_map_info(addr)
        except:
            address='You did not provide any company address.'
        result, probability = get_prediction(text)
 
        return render_template('forms/Home.html', result=result, prob = probability,mis=mistake, map=address)


if __name__ == '__main__':
    app.run(debug=True)
    
    
