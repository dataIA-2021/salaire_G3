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

class Scrapper():

    template = 'https://www.indeed.fr/jobs?q={}&l={}' # Constante de classe
    job = ['developer','data scientist','data analyst','business intelligence']
    city = ['Paris','Lyon','Toulouse','Nantes','Bordeaux','Tours']

    # constructeur
    def __init__(self,position='data scientist',location='Paris',allPages=False):
        
        self.position = position
        self.location = location
        self.records = [] # init de la liste des enregistrements
        
        url = self.getUrl(self.template)

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
                
            # Si toutes les pages (allPages) non precise, sortie
            if allPages == False:
                break
            
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
        company = topCard.find('div', 'companyInfo').find('span','companyName').text # Nom de l'entreprise
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
    
    def exportJSONFile(self):
        
        output = []
        
        # Mise en forme JSON et insertion dans une liste avant export
        for record in self.records:
            data = {
                '_id': {
                    '$oid':record[0]
                },
                'job_title': record[1],
                'company': record[2],
                'job_location': record[3],
                'salary': record[4],
                'summary': record[5],
                'post_date': record[6]
            }
            output.append(data)
        
        # Export du fichier JSON avec la liste output
        with open('data.json', 'w',encoding='utf-8') as f:
            json.dump(output,f, indent = 4,ensure_ascii=False)