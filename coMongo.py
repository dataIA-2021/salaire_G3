# -*- coding: utf-8 -*-
"""
Created on Wed Feb  9 12:23:13 2022

@author: François
"""

from pymongo import MongoClient
# import yaml

# with open ('acces.yml', 'r') as f:
#     conf = yaml.safe_load(f)
# my = conf['MONGO']
    
"""Connection MongoDB"""
client = MongoClient('mongodb://%s:%s' % ('127.0.0.1','27017'))
db = client['grp3_salaire']
collec = db['test_pirateur']

# uri = "mongodb://data-salaries:b8FVZBOSzwVrx3Fgbtbb7lDCTO0eDQN5mf0beVoZDPezcZWcWNa8mX5gxLm0sx9iGCvulnMY30uiYP4oEdVYpw==@data-salaries.mongo.cosmos.azure.com:10255/?ssl=true&retrywrites=false&replicaSet=globaldb&maxIdleTimeMS=120000&appName=@data-salaries@"
# client = MongoClient(uri)
# db = client['detect_salaire']
# collec = db['data']

# db.list_collection_names()
# collec.drop()

kek = {
    "_id": "3d5487bc57a59ba4",
    "job_title": "nouveauData Scientist Big Data (F/H)",
    "company": "AXA",
    "job_location": "Nanterre (92)",
    "salary": "",
    "summary": "Gestion de projet data et data science. Animation de formations data d’acculturation et de formations professionnalisantes internes sur les outils et pratiques…",
    "post_date": "Postedil y a 1 jour"
}

cond = collec.count_documents({ "_id": kek["_id"]})
if cond == 0:
    collec.insert_one(kek)
        