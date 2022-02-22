# -*- coding: utf-8 -*-
"""
Created on Tue Feb 22 10:51:21 2022

@author: François
"""

import requests
from bs4 import BeautifulSoup as BS

url_b = 'https://fr.indeed.com/voir-emploi?jk=%s'%(record[0])

response = requests.get(url_b)
soup = BS(response.text, 'html.parser')
comment = soup.find('div','jobsearch-jobDescriptionText').text
# text = comment.find('div')
print(comment)