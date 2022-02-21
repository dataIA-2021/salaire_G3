from flask import Flask, render_template,request
import pickle

app = Flask(__name__)
# TODO Chargement du modele regression
# model = pickle.load(open('model.pkl', 'rb'))

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == "__main__":
    app.run()
    
