# -*- coding: utf-8 -*-
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
import statistics
import numpy as np
import re


class Scrapper():
    
    # Constante de classe
    TEMPLATE = 'https://www.indeed.fr/jobs?q={}&l={}' 
    JOBS = jobs.getListJobs() # Import des jobs
    # dictionnaire de compétence
    DICTI_TECH = {0: 'python', 1: 'html', 2: 'css', 3: 'java', 4: 'flask',
             5: 'django', 6: 'react', 7: 'java script', 8: 'nodejs',
             9: 'Cobol', 10: 'wordpress', 11: 'php', 12: 'redux',
             13: 'cordova', 14: 'es6', 15: 'mongodb', 16: 'mysql',
             17: 'sass', 18: 'tailwind', 19: 'keycloak', 20: 'Angular 12',
             21: 'Bootstrap', 22: 'c#', 23: 'postgresql', 24: 'elastic search',
             25: 'kibana', 26: 'apache hadoop', 27: 'azure', 28: 'aws',
             29: 'google', 30: 'vba', 31: 'sql', 32: 'windev',
             33: 'excel', 34: 'webdesign', 35: 'ajax', 36: 'powerbi',
             37: 'rpgle', 38: 'mak', 39: 'mec', 40: 'ssis', 41: 'pbi',
             42: 'stream', 43: 'db400', 44: 'anglais', 45: 'typescript',
             46: 'angularjs', 47: 'git', 48: 'vuejs', 49: 'nuxtjs', 50: 'c\\+\\+',
             51: 'docker', 52: 'network', 53: 'ci/cd', 54: 'golang',
             55: 'sass', 56: 'agile', 57: 'scrum', 58: 'kanban',
             59: 'dax', 60: 'qlik', 61: 'spark', 62: 'hive',
             63: 'presto', 64: 'google analytic', 65: ' r '}

    
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
        
        url_b = 'https://fr.indeed.com/voir-emploi?jk=%s' % (_id)
        # print(url_b)
        response = requests.get(url_b)
        _soup = BeautifulSoup(response.text, 'html.parser')
        comment = _soup.find('div', 'jobsearch-jobDescriptionText').text
        
        # Recherche de la présence des différentes compétences, présente : 1 absente : 0
        for i in DICTI_TECH:
            if bool(re.search('(^.*'+DICTI_TECH[i]+'.*$)', str(comment.lower()))) == True:
                data[DICTI_TECH[i]] = 1
            else : 
                data[DICTI_TECH[i]] = 0
        
        # recherche du type de job en télétravail, hybride ou présence si le clean_location est vide
        if (data['clean_location'] == '')==True:
            remote = re.findall(r"t[eéè]l[eéè]travail", comment)
            if remote:
                data['remote']=1
                data['clean_location']= remote[0]
            else:
                hybrid = re.findall(r'hybrid|hybride', comment)
                if hybrid:
                    data['hybrid']=1
                    data['clean_location']= hybrid[0]
                else:
                    data['presence']=1    
                    

    # detection du salaire dans le bloc de droite
        # pour les salaires sous la forme 32 - 32 k€
        if (data['salary'] == '')==True:
            if bool(re.findall(r"\d{2} - \d{2} k€", str(comment.lower())))==True:
                salary_right = re.findall(r"\d{2} - \d{2} k€", str(comment.lower()))
                salary_split = str(str(salary_right).split())
                salary_split = salary_split.replace('k€', '')
                first_sal = int(salary_split[4]+salary_split[5])*1000
                second_sal = int(salary_split[15]+salary_split[16])*1000
                sal = (first_sal+second_sal)/2
                sal = round(sal)
                data['min_salary'] = first_sal
                data['max_salary'] = second_sal
                data['annual_salary'] = sal
                data['monthly_salary'] = round(sal/12)
            # pour les salaires sour la forme 32 k€
            elif bool(re.findall(r"\d{2} k€", str(comment.lower())))==True:
                salary_right = re.findall(r"\d{2} k€", str(comment.lower()))
                salary_split = str(str(salary_right).split())
                salary_split = salary_split.replace('k€', '')
                sal = int(salary_split[4]+salary_split[5])*1000
                data['min_salary'] = data['max_salary'] = sal
                data['annual_salary'] = sal
                data['monthly_salary'] = round(sal/12)
            #  pour les salaires sous la forme 1400,00 €, 1400,00€, 1400 € ou 1400€
            else:
                comment_ = re.sub(r',\d+','',comment)
                salaire = re.findall(r'(\d+ \d+) €|(\d+ \d+)€|(\d+)€|(\d+) €', comment_)
                # si salaire contient qqch
                if salaire:                
                    z = len(salaire)
                    # et que ça longueur est supérieur à 1
                    if z>1:
                        first = salaire[0]
                        for i in first:
                            if (i=='')==True:
                                continue
                            else:
                                min_sal = i
                                min_sal = min_sal.replace(' ','')
                                min_sal= int(min_sal)
                        second = salaire[1]
                        for i in second:
                            if (i=='')==True:
                                continue
                            else:
                                max_sal = i
                                max_sal = max_sal.replace(' ','')
                                max_len = len(max_sal)
                                max_sal= int(max_sal)
                        #  sal <= 3 permet de vérifier que le chiffre vérifier soit un nombre pouvant correspondre à un salaire mensuelle au minimum
                        if sal<=3:
                            continue
                        # max_len>4 pour vérifier si c'est un salaire à l'année
                        elif max_len>4:                   
                            data['min_salary'] = min_sal
                            data['max_salary'] = max_sal
                            data['annual_salary']= round((data['max_salary']+data['min_salary'])/2)
                        else:
                            data['min_salary'] = min_sal*12
                            data['max_salary'] = max_sal*12
                            data['annual_salary'] =  round((data['max_salary']+data['min_salary'])/2)
                    else:
                        #  répétitiion de la structure précédente
                        first = salaire[0]
                        for i in first:
                            if (i=='')==True:
                                continue
                            else:
                                sal = i
                                sal = sal.replace(' ','')
                                sal_len = len(sal)
                                sal= int(sal)
                        if sal<=3:
                            continue
                        elif sal_len>4:                   
                            data['min_salary'] = sal
                            data['max_salary'] = sal
                            data['annual_salary'] = data['mean_salary'] = data['per_year'] = round((data['max_salary']+data['min_salary'])/2)
                        else:
                            data['min_salary'] = sal*12
                            data['max_salary'] = sal*12
                            data['annual_salary'] = data['mean_salary'] = data['per_year'] = round((data['max_salary']+data['min_salary'])/2)
                else:
                    data['salary']=''
        
        record = (_id,job_title, company, job_location,salary, summary,post_date,comment)
        return record
        
    
    def showRecords(self):
        print(self.records)
    
    def sleepForRandomInterval(self):
        seconds = random() * 10
        sleep(seconds)
    
    def exportMongoDB(self):
        
        # Mise en forme JSON et insertion dans une liste avant export
        for record in self.records:
            data = {
                '_id': record[0],
                'job_title': record[1],
                'company': record[2],
                'job_location': record[3],
                'clean_location': '',
                'presence':0,
                'remote':0,
                'hybrid':0,
                'salary': record[4],
                'interval':'',
                # 'per_hour': 0,
                # 'per_day': 0,
                # 'per_week': 0,
                # 'per_month': 0,
                # 'per_year': 0,
                'min_salary': 0,
                'max_salary': 0,
                'mean_salary': 0,
                'monthly_salary': 0,
                'annual_salary': 0,                
                'summary': record[7],
                'post_date': record[6],
                'python': '',
                'html': '',
                'css': '',
                'java': '',
                'flask': '',
                'django': '',
                'react': '',
                'java script': '',
                'nodejs': '',
                'Cobol': '',
                'wordpress': '',
                'php': '',
                'redux': '',
                'cordova': '',
                'es6': '',
                'mongodb': '',
                'mysql': '',
                'sass': '',
                'tailwind': '',
                'keycloak': '',
                'Angular 12': '',
                'Bootstrap': '',
                'c#': '',
                'postgresql': '',
                'elastic search': '',
                'kibana': '',
                'apache hadoop': '',
                'azure': '',
                'aws': '',
                'google': '',
                'vba': '',
                'sql': '',
                'windev': '',
                'excel': '',
                'webdesign': '',
                'ajax': '',
                'powerbi': '',
                'rpgle': '',
                'mak': '',
                'mec': '',
                'ssis': '',
                'pbi': '',
                'stream': '',
                'db400': '',
                'anglais': '',
                'typescript': '',
                'angularjs': '',
                'git': '',
                'vuejs': '',
                'nuxtjs': '',
                'c\\+\\+': '',
                'docker': '',
                'network': '',
                'ci/cd': '',
                'golang': '',
                'sass': '',
                'agile': '',
                'scrum': '',
                'kanban': '',
                'dax': '',
                'qlik': '',
                'spark': '',
                'hive': '',
                'presto': '',
                'google analytic': '',
                ' r ': ''
            }
            data = self.cleanRecord(data)
            
            if self.collec.count_documents({ "_id": record[0]}) == 0:
                self.collec.insert_one(data)
    
    # Nettoyage des enregistrement, partie de Tess        
    def cleanRecord(self,data):
        
        # Traitement sur les salaires
        salary = data['salary']
        
        # Si salary est renseigne           

        if salary:
            # Temps de travail
            if 'par heure' in salary:
                data['interval'] = 'per_hour'
            elif 'par jour' in salary:
                data['interval'] = 'per_day'
            elif 'par semaine' in salary:
                data['interval'] = 'per_week'
            elif 'par mois' in salary:
                data['interval'] = 'per_month'
            elif 'par an' in salary:
                data['interval'] = 'per_year'
    
        
            salary = re.sub(r'[a-zA-Z]|[€]|[ ]','', salary)
            salary = re.sub(r'[,]','.', salary)
            
            data['min_salary'] = salary.split('-')[0]
            data['min_salary'] = float(data['min_salary']) # Convertir en numerique
        
        
            if len(salary.split('-')) > 1:
                
                data['max_salary'] = salary.split('-')[1]
                data['max_salary'] = float(data['max_salary']) # Convertir en numerique
                
            else:
                
                data['max_salary'] = data['min_salary']
                
            
            data['mean_salary'] = statistics.mean([data['min_salary'],data['max_salary']])
            data['mean_salary'] = round(data['mean_salary'],2)
                    
            # ],[minimum*1825, minimum*260, minimum*52, minimum*12]
            # Temps de travail
            if data['interval'] == 'per_hour':
                data['annual_salary'] = data['mean_salary'] * 1607 # Heures officielles par an
            elif data['interval'] == 'per_day':
                data['annual_salary'] = data['mean_salary'] * 5 * 52
            elif data['interval'] == 'per_week':
                data['annual_salary'] = data['mean_salary'] * 52
            elif data['interval'] == 'per_month':
                data['annual_salary'] = data['mean_salary'] * 12
                
            data['annual_salary'] = round(data['annual_salary'],2)
        
        location = data['job_location'].lower()

        travail_type = location

        location = location.split('.')[0]

        location = location.replace('télétravail', '')        
        location = location.replace('temporaire', '')
        location = location.replace('hybrid remote', '')
        location = location.replace('in', '')
        location = location.replace('+ lieu', '')
        location = location.replace('lieux', '')        
        location = location.replace('+lieu', '')
        location = location.split('.')[0]

        location = re.sub(r'.\d+.|[+]|[\']|[ ]','', location)

        location = location.split('-')[0]

        # travail_type = travail_type.split()

        remote = re.findall(r"t[eéè]l[eéè]travail", travail_type)
        if remote:
            data['remote']=1
        else:
            hybrid = re.findall(r'hybrid|hybride', travail_type)
            if hybrid:
                data['hybrid']=1
            else:
                data['presence']=1
        
        return data