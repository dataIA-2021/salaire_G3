import re

location = 'Hybrid remote Paris'

# Minuscules
location = location.lower()

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

print(location)