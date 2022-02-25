""" 
Author: Victorien
Date: 17/02  
Description:
    - Scrapping indeed en fonction d'un poste et/ou d'une adresse
    - creation d'une liste des jobs & infos
Args :
    - position : poste recherche
    - location : ville recherche
    - allPages : 
        - True pour parcourir toutes les pages
        - False pour parcourir uniquement la premiere page
"""
import requests
from bs4 import BeautifulSoup
import json
import csv
from pymongo import MongoClient
from random import random
from time import sleep
#from torrequest import TorRequest
import yaml
import jobs
#import statistics
import numpy as np
import pandas as pd
import re

class Scrapper():
    
    # Constante de classe
    TEMPLATE = 'https://www.indeed.fr/jobs?q={}&l={}' 
    JOBS = jobs.getListJobs() # Import des jobs
    
    # constructeur
    def __init__(self,allPages):
        
        self._allPages = allPages
        
        # Connection MongoDB
        with open('config.yaml','r') as f:
            config = yaml.safe_load(f)
        
        mg = config['MONGODB_TEST'] # Changer ici pour TEST/PROD
        connexion = f"mongodb://{mg['ip']}:{mg['port']}"
        client = MongoClient(connexion)
        db = client[mg['client']]
        self.collec = db[mg['db']]

    def launch(self):
        
        if self._allPages == True:
            for job in self.JOBS:
                self.browseWeb(job)
        else:
            self.browseWeb(self.JOBS[0]) # Le premier job par defaut
                
        print('Fin webscrapping')
        
    def browseWeb(self,job):
        self.position = job
        self.location = 'France' # par defaut
        self.records = [] # init de la liste des enregistrements
        nbPage = 1
        
        url = self.getUrl(self.TEMPLATE)
        print(url)
        
        # Par defaut, parcours de toutes les pages 
        while True:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            mosaic = soup.find('div','mosaic-provider-jobcards')

            self.cards = mosaic.find_all('a','tapItem')

            # Construction du jeu d'enregistrement
            for card in self.cards:
                record = self.getRecord(card)
                self.records.append(record)
                #self.sleepForRandomInterval()
                
            self.exportMongoDB()
            self.records.clear() # Reinitialisation des records
            
            # Si toutes les pages (allPages) non precise, sortie
            if self._allPages == False:
                break
            else: 
                self.sleepForRandomInterval() # pause avant la prochaine page
                nbPage += 1
                
            try:
                url = 'https://www.indeed.fr' + soup.find('a', {'aria-label': 'Suivant'}).get('href')
            except AttributeError:
                break
            
        print(nbPage,' page(s) scrappée(s)') # log

    def getUrl(self,template):
        position = self.position.replace(' ', '+')
        location = self.location.replace(' ', '+')
        url = template.format(position, location)
        return url
    
    def getRecord(self,card):
        # Separation d'une carte indeed en 2 parties
        topCard = card.find('td','resultContent')
        botCard = card.find('table','jobCardShelfContainer')
        
        _id = card['data-jk']
        
        job_pan = topCard.find('h2','jobTitle')
        
        # Cas d'une nouvelle annonce
        if len(job_pan.find_all('span')) > 1:
            job_title = job_pan.find_all('span')[1].text
        else:
            job_title = topCard.find('h2','jobTitle').text # Titre du poste
        
        # Correction bug si non presence de la company
        try:
            company = topCard.find('div', 'companyInfo').find('span','companyName').text # Nom de l'entreprise
        except AttributeError:
            company = ''
        
        
        job_location = topCard.find('div', 'companyLocation').text # localisation
        
        salary = topCard.find('div','salary-snippet') # Dans le cas d'une offre avec le salaire precise
        if salary: # Le salaire n'est pas toujours present sur les offres...
            salary = salary.text.replace(u'\xa0', u' ')
        else:
            salary = ''
            
        summary = botCard.find('div','job-snippet').text.strip().replace('\n', ' ') # Description du poste
        post_date = botCard.find('span', 'date').text # Date de publication
        
        record = (_id,job_title, company, job_location,salary, summary,post_date)
        return record
    
    def exportCSV(self):
        # save the job data
        with open('results.csv', 'w', newline='', encoding='utf-8') as f: #ISO-8859-1
            writer = csv.writer(f)
            # Titre
            writer.writerow(['_id','Titre du poste', 'Entreprise', 'Adresse', 'Salaire','Decription','date'])
            # Ecriture
            writer.writerows(self.records)
    
    def showRecords(self):
        print(self.records)
    
    def toJSON(self,text): # Obselete ?
        relevant = text[text.index('=')+1:] #removes = and the part before it
        data = json.loads(relevant) #a dictionary!
        print(json.dumps(data, indent=4))
    
    def sleepForRandomInterval(self):
        seconds = random() * 10
        sleep(seconds)
    
    def exportMongoDB(self):
        
        # Mise en forme JSON et insertion dans une liste avant export
        for record in self.records:
            data = {
                '_id':record[0],
                'job_title': record[1],
                'company': record[2],
                'job_location': record[3],
                'clean_location':'',
                'salary': record[4],
                'per_hour':0,
                'per_day':0,
                'per_week':0,
                'per_month':0,
                'per_year':0,
                'min_salary':0,
                'max_salary':0,
                'mean_salary':0,
                'monthly_salary':0,
                'annual_salary':0,
                'summary': record[5],
                'post_date': record[6]
            }
            data = self.cleanRecord(data)
            print(data)
            #if self.collec.count_documents({ "_id": record[0]}) == 0:
                #self.collec.insert_one(data)
    
    # Nettoyage des enregistrement, partie de Tess        
    def cleanRecord(self,data):
        
        # Traitement sur les salaires
        salary = data['salary']
        
        #values par heure, par jour, par semaine, par mois, par an
        
        # Calcul salaire mensuel
        
        per_hour = 'par heure' in salary
        per_day = 'par jour' in salary
        per_week = 'par semaine' in salary #par mois is a default value
        per_month = 'par semaine' in salary
        per_year = 'par an' in salary
            
        # Traitement sur les salaires
            # Si salary est renseigne
        if salary:
            # Temps de travail
            if 'par heure' in salary:
                data['per_hour'] = 1
            elif 'par jour' in salary:
                data['per_day'] = 1
            elif 'par semaine' in salary:
                data['per_week'] = 1
            elif 'par mois' in salary:
                data['per_month'] = 1
            elif 'par an' in salary:
                data['per_year'] = 1
                
            #Replacement
            
            #removing all characters[a-z] except figures[0-9], regex
            salary_range = salary
            salary_range = salary.replace(',', '')            
            salary_range = salary.replace(r'[a-zA-Z]|[€]|[ ]', '')
            
            #min/max
            #min_salary
            
            # min/max
            min_salary = salary_range.split('-')[0]    
                               
            #converting to numeric values, float type
            
            minimum = pd.to_numeric(min_salary, errors='coerce').astype(float)
            
            #Annual minimum salary, default value = per_year
            
            data['minimum_annual_salary'] = np.select([per_hour, per_day, per_week, per_month],[minimum*1825, minimum*260, minimum*52, minimum*12], default=minimum)            
            #monseul minimum, default value = per_month            
            data['minimum_monthly_salary'] = np.select([per_hour, per_day, per_week, per_year],[minimum*1825, minimum*260, minimum*52, minimum/12], default=minimum)
                        
            #maximum_salary
            
            if len(salary_range.split('-')) > 1:
                max_salary = salary_range.split('-')[1]
                
                #numeric value
                
                maximum = pd.to_numeric(max_salary, errors='coerce').astype(float)
                                              
                # moyenne salaire
                #numeric value
                
                ##Maximum annual & monthly value
                
                data['maximum_annual_salary'] = np.select([per_hour, per_day, per_week, per_month],[maximum*1825, maximum*260, maximum*52, maximum*12], default=maximum)
                #mensuel, maximum
                data['maximum_monthly_salary'] = np.select([per_hour, per_day, per_week, per_year],[maximum*1825, maximum*260, maximum*52, maximum/12], default=maximum)
                
                #salaire moyenne
                
                # Annual average salary; (min + max)/2
                data['annual_average_salary'] = (data['minimum_annual_salary'] + data['maximum_annual_salary'])/2
                
                #Salaire moyenne mensuel
                
                
                #mensuel, maximum
                data['maximum_monthly_salary'] = np.select([per_hour, per_day, per_week, per_year],[maximum*1825, maximum*260, maximum*52, maximum/12], default=maximum)
                
                #monseul moyenne
                data['monthly_average_salary'] = (data['minimum_monthly_salary'] + data['maximum_monthly_salary'])/2
                
                #data['annual_salary'] = 0 # TODO : A revoir par Tess
                
        # Traitement de l'adresse
        
        data['job_location'] = data['job_location'].split('.')[0]

          
        data['job_location'] = data['job_location'].replace('télétravail', '')        
        data['job_location'] = data['job_location'].replace('temporaire', '')
        data['job_location'] = data['job_location'].replace('hybrid remote', '')
        data['job_location'] = data['job_location'].replace('in', '')
        data['job_location'] = data['job_location'].replace('+ lieu', '')
        data['job_location'] = data['job_location'].replace('lieux', '')        
        data['job_location'] = data['job_location'].replace('+lieu', '')
        data['job_location'] = data['job_location'].split('.')[0]
        
        
        location_data = re.sub(r'.\d+.|[+]|[\']|[ ]','', data['job_location'])
        
        data['clean_location'] = location_data.split('-')[0]
            
        return data
        
