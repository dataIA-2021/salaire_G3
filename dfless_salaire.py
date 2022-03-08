# -*- coding: utf-8 -*-
"""
Created on Thu Feb 24 12:11:56 2022

@author: François
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Feb 22 10:51:21 2022

@author: François
"""
# import pprint
# import pandas as pd
# import numpy as np
# import csv

# re.escape('c++')

import re
import requests
from bs4 import BeautifulSoup as BS

# dictionnaire de compétence
dicti_tech = {0: 'python', 1: 'html', 2: 'css', 3: 'java', 4: 'flask',
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

url = 'https://fr.indeed.com/emplois?q=data%20analyst&vjk=7f246b193949b40d'

records = []


def getRecord(card):
        # Separation d'une carte indeed en 2 parties
        topCard = card.find('td', 'resultContent')
        botCard = card.find('table', 'jobCardShelfContainer')

        _id = card['data-jk']
        job_title = topCard.find('h2', 'jobTitle').text  # Titre du poste

        # Correction bug si non presence de la company
        try:
            company = topCard.find('div', 'companyInfo').find(
                'span', 'companyName').text  # Nom de l'entreprise
        except AttributeError:
            company = ''

        job_location = topCard.find(
            'div', 'companyLocation').text  # localisation

        # Dans le cas d'une offre avec le salaire precise
        salary = topCard.find('div', 'salary-snippet')
        if salary:  # Le salaire n'est pas toujours present sur les offres...
            salary = salary.text.replace(u'\xa0', u' ')
        else:
            salary = ''

        # Description du poste
        summary = botCard.find(
            'div', 'job-snippet').text.strip().replace('\n', ' ')
        post_date = botCard.find('span', 'date').text  # Date de publication

        record = (_id, job_title, company, job_location,
                  salary, summary, post_date)
        return record


print(url)
response = requests.get(url)
soup = BS(response.text, 'html.parser')
mosaic = soup.find('div','mosaic-provider-jobcards')

cards = mosaic.find_all('a','tapItem')
# Construction du jeu d'enregistrement
for card in cards:
    record = getRecord(card)
    records.append(record)
    url_b = 'https://fr.indeed.com/voir-emploi?jk=%s' % (record[0])
    print(url_b)
    response = requests.get(url_b)
    _soup = BS(response.text, 'html.parser')
    comment = _soup.find('div', 'jobsearch-jobDescriptionText').text
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
        'per_hour': 0,
        'per_day': 0,
        'per_week': 0,
        'per_month': 0,
        'per_year': 0,
        'min_salary': 0,
        'max_salary': 0,
        'mean_salary': 0,
        'monthly_salary': 0,
        'annual_salary': 0,
        'summary': comment,
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
    
    # Recherche de la présence des différentes compétences, présente : 1 absente : 0
    for i in dicti_tech:
        if bool(re.search('(^.*'+dicti_tech[i]+'.*$)', str(comment.lower()))) == True:
            data[dicti_tech[i]] = 1
        else : 
            data[dicti_tech[i]] = 0
    
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
            data['per_hour'] = round(data['mean_salary']/1607, 2)
            data['per_day'] = round((data['mean_salary']/52)/5,2)
            data['per_month'] = data['monthly_salary']
            data['per_week'] = round(data['per_month']/4.3, 2)
        # pour les salaires sour la forme 32 k€
        elif bool(re.findall(r"\d{2} k€", str(comment.lower())))==True:
            salary_right = re.findall(r"\d{2} k€", str(comment.lower()))
            salary_split = str(str(salary_right).split())
            salary_split = salary_split.replace('k€', '')
            sal = int(salary_split[4]+salary_split[5])*1000
            data['min_salary'] = data['max_salary'] = sal
            data['annual_salary'] = sal
            data['monthly_salary'] = round(sal/12)
            data['per_hour'] = round(data['mean_salary']/1607, 2)
            data['per_day'] = round((data['mean_salary']/52)/5,2)
            data['per_month'] = data['monthly_salary']
            data['per_week'] = round(data['per_month']/4.3, 2)
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
                    data['per_hour'] = round(data['mean_salary']/1607, 2)
                    data['per_day'] = round((data['mean_salary']/52)/5,2)
                    data['per_month'] = data['monthly_salary']
                    data['per_week'] = round(data['per_month']/4.3, 2)
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
                    data['per_hour'] = round(data['mean_salary']/1607, 2)
                    data['per_day'] = round((data['mean_salary']/52)/5,2)
                    data['per_month'] = data['monthly_salary']
                    data['per_week'] = round(data['per_month']/4.3, 2)
            else:
                data['salary']=''