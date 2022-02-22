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
            
            print(nbPage,' page(s) terminée(s)') # log
            
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
                'salary': record[4],
                'summary': record[5],
                'post_date': record[6]
            }
            
            if self.collec.count_documents({ "_id": record[0]}) == 0:
                self.collec.insert_one(data)
        
