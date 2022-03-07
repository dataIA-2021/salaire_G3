import re
import numpy as np
import statistics

salary = '500 € par semaine'

data = {
    'min_salary':0,
    'max_salary':0,
    'mean_salary':0,
    'mean_annual':0,
    'interval':''
}

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
        data['mean_annual'] = data['mean_salary'] * 1607 # Heures officielles par an
    elif data['interval'] == 'per_day':
        data['mean_annual'] = data['mean_salary'] * 5 * 52
    elif data['interval'] == 'per_week':
        data['mean_annual'] = data['mean_salary'] * 52
    elif data['interval'] == 'per_month':
        data['mean_annual'] = data['mean_salary'] * 12
        
    data['mean_annual'] = round(data['mean_annual'],2)
        
        
        #maximum = pd.to_numeric(max_salary, errors='coerce').astype(float)
                                      
        # moyenne salaire
        #numeric value
        
        ##Maximum annual & monthly value
        
        #data['maximum_annual_salary'] = np.select([per_hour, per_day, per_week, per_month],[maximum*1825, maximum*260, maximum*52, maximum*12], default=maximum)
        #mensuel, maximum
        #data['maximum_monthly_salary'] = np.select([per_hour, per_day, per_week, per_year],[maximum*1825, maximum*260, maximum*52, maximum/12], default=maximum)
        
        #salaire moyenne
        
        # Annual average salary; (min + max)/2
        #data['annual_average_salary'] = (data['minimum_annual_salary'] + data['maximum_annual_salary'])/2
        
        #Salaire moyenne mensuel
        
        
        #mensuel, maximum
        #data['maximum_monthly_salary'] = np.select([per_hour, per_day, per_week, per_year],[maximum*1825, maximum*260, maximum*52, maximum/12], default=maximum)
        
        #monseul moyenne
        #data['monthly_average_salary'] = (data['minimum_monthly_salary'] + data['maximum_monthly_salary'])/2
        
        #data['annual_salary'] = 0 # TODO : A revoir par Tess
            
