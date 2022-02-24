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
dicti = {0: 'python', 1: 'html', 2: 'css', 3: 'java', 4: 'flask',
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

url = 'https://fr.indeed.com/Emplois-developpeur?vjk=05c5d938a1fe276e'

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
    for i in dicti:
        if bool(re.search('(^.*'+dicti[i]+'.*$)', str(comment.lower()))) == True:
            data[dicti[i]] = 1
        else : 
            data[dicti[i]] = 0


