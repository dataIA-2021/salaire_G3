from flask import Flask, render_template, request
import pickle
from sklearn.pipeline import Pipeline
import pandas as pd
from sklearn.metrics import mean_absolute_error

app = Flask(__name__)


# Chargement du modele regression
model = pickle.load(open("model.pkl", "rb"))


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/prediction")
def prediction():
    global n, pipe
    city = request.args.get("city")
    city = city.lower() # force minuscules
    contract = request.args.get("contract")
    exp = int(request.args.get("exp"))
    
    hybrid = 0
    presence = 0
    remote = 0
    location = request.args.get("location")
    if location == 'presence':
        presence = 1
    elif location == 'hybrid':
        hybrid = 1
    elif location == 'remote':
        remote = 1
        
    interval = request.args.get("interval")
    job = request.args.get("job")
    
    gestion_projet = request.args.get("gestion_projet")
    big_data = request.args.get("big_data")
    front_back = request.args.get("front_back")
    data_analytics = request.args.get("data_analytics")

    dic = {
        'clean_location':city,
        'contract':contract,
        'exp':exp,
        'hybrid':hybrid,
       'interval': interval,
       'job_clean':job,
       'presence':presence,
       'remote':remote,
       'Gestion_Projet':gestion_projet,
       'Big_Data':big_data,
       'Front_Back':front_back,
       'Data_Analytics':data_analytics
    }
    df_predict = pd.DataFrame(dic, index=[0])
    y = model.predict(df_predict)
    
    # n+=1
    # result= {'sms':sms, 'result':['ham','spam'][int(y[0])], 'n':n}

    result = {"salary": y.tolist()}
    return result


if __name__ == "__main__":
    app.run(debug=True)
