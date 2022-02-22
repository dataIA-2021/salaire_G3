# -*- coding: utf-8 -*-
"""
Created on Tue Feb 22 10:51:21 2022

@author: François
"""

import requests
from bs4 import BeautifulSoup as BS

url = 'https://fr.indeed.com/voir-emploi?jk=daf6f8c39149c15e'

response = requests.get(url)
soup = BS(response.text, 'html.parser')
comment = soup.find('div','jobsearch-jobDescriptionText').text
# text = comment.find('div')
print(comment)