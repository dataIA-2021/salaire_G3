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

# from torrequest import TorRequest
import yaml
import jobs
import statistics
import numpy as np
import re


class Scrapper:

    # Constante de classe
    TEMPLATE = "https://www.indeed.fr/jobs?q={}&l={}"
    JOBS = jobs.getListJobs()  # Import des jobs
    # dictionnaire de compétence
    DICTI_TECH = {
        0: "python",
        1: "html",
        2: "css",
        3: "java",
        4: "flask",
        5: "django",
        6: "react",
        7: "java script",
        8: "nodejs",
        9: "Cobol",
        10: "wordpress",
        11: "php",
        12: "redux",
        13: "cordova",
        14: "es6",
        15: "mongodb",
        16: "mysql",
        17: "sass",
        18: "tailwind",
        19: "keycloak",
        20: "Angular 12",
        21: "Bootstrap",
        22: "c#",
        23: "postgresql",
        24: "elastic search",
        25: "kibana",
        26: "apache hadoop",
        27: "azure",
        28: "aws",
        29: "google",
        30: "vba",
        31: "sql",
        32: "windev",
        33: "excel",
        34: "webdesign",
        35: "ajax",
        36: "powerbi",
        37: "rpgle",
        38: "mak",
        39: "mec",
        40: "ssis",
        41: "pbi",
        42: "stream",
        43: "db400",
        44: "anglais",
        45: "typescript",
        46: "angularjs",
        47: "git",
        48: "vuejs",
        49: "nuxtjs",
        50: "c\\+\\+",
        51: "docker",
        52: "network",
        53: "ci/cd",
        54: "golang",
        55: "sass",
        56: "agile",
        57: "scrum",
        58: "kanban",
        59: "dax",
        60: "qlik",
        61: "spark",
        62: "hive",
        63: "presto",
        64: "google analytic",
        65: " r ",
    }

    # constructeur
    def __init__(self, allPages):

        self._allPages = allPages

        # Connection MongoDB
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)
        mg = config["MONGODB_TEST"]  # Changer ici pour TEST/PROD
        connexion = f"mongodb://{mg['ip']}:{mg['port']}"
        client = MongoClient(connexion)
        db = client[mg["client"]]
        self.collec = db[mg["db"]]

    def launch(self):

        if self._allPages == True:
            for job in self.JOBS:
                self.browseWeb(job)
        else:
            self.browseWeb(self.JOBS[0])  # Le premier job par defaut
        print("Fin webscrapping")

    def browseWeb(self, job):
        self.position = job
        self.location = "France"  # par defaut
        self.records = []  # init de la liste des enregistrements
        nbPage = 1

        url = self.getUrl(self.TEMPLATE)
        print(url)

        # Par defaut, parcours de toutes les pages
        while True:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")

            mosaic = soup.find("div", "mosaic-provider-jobcards")

            self.cards = mosaic.find_all("a", "tapItem")

            # Construction du jeu d'enregistrement
            for card in self.cards:
                record = self.getRecord(card)
                self.records.append(record)
                
            self.exportMongoDB()
            self.records.clear()  # Reinitialisation des records

            # Si toutes les pages (allPages) non precise, sortie
            if self._allPages == False or nbPage > 20:
                break
            else:
                self.sleepForRandomInterval()  # pause avant la prochaine page
                print('page:',nbPage)
                nbPage += 1
            try:
                url = "https://www.indeed.fr" + soup.find("a", {"aria-label": "Suivant"}).get("href")
            except AttributeError:
                break
        print(nbPage, " page(s) scrappée(s)")  # log

    def getUrl(self, template):
        position = self.position.replace(" ", "+")
        location = self.location.replace(" ", "+")
        url = template.format(position, location)
        return url

    def getRecord(self, card):
        # Separation d'une carte indeed en 2 parties
        topCard = card.find("td", "resultContent")
        botCard = card.find("table", "jobCardShelfContainer")

        _id = card["data-jk"]

        job_pan = topCard.find("h2", "jobTitle")

        # Cas d'une nouvelle annonce
        if len(job_pan.find_all("span")) > 1:
            job_title = job_pan.find_all("span")[1].text
        else:
            job_title = topCard.find("h2", "jobTitle").text  # Titre du poste
        # Correction bug si non presence de la company
        try:
            company = (
                topCard.find("div", "companyInfo").find("span", "companyName").text
            )  # Nom de l'entreprise
        except AttributeError:
            company = ""
        job_location = topCard.find("div", "companyLocation").text  # localisation

        salary = topCard.find(
            "div", "salary-snippet"
        )  # Dans le cas d'une offre avec le salaire precise
        if salary:  # Le salaire n'est pas toujours present sur les offres...
            salary = salary.text.replace("\xa0", " ")
        else:
            salary = ""
        summary = (
            botCard.find("div", "job-snippet").text.strip().replace("\n", " ")
        )  # Description du poste
        post_date = botCard.find("span", "date").text  # Date de publication

        #self.sleepForRandomInterval()

        url_b = "https://fr.indeed.com/voir-emploi?jk=%s" % (_id)
        # print(url_b)
        response = requests.get(url_b)
        _soup = BeautifulSoup(response.text, "html.parser")
        comment = _soup.find("div", "jobsearch-jobDescriptionText").text.lower()

        record = (
            _id,
            job_title,
            company,
            job_location,
            salary,
            summary,
            post_date,
            comment,
        )
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
                "_id": record[0],
                "job_title": record[1],
                "job_clean": "",
                "contract": "",
                "exp": 1,  # par defaut
                "company": record[2],
                "job_location": record[3],
                "clean_location": "",
                "presence": 0,
                "remote": 0,
                "hybrid": 0,
                "salary": record[4],
                "interval": "",
                "min_salary": 0,
                "max_salary": 0,
                "mean_salary": 0,
                "monthly_salary": 0,
                "annual_salary": 0,
                "summary": record[7],
                "post_date": record[6],
                "clean_date": 0,
                "python": "",
                "html": "",
                "css": "",
                "java": "",
                "flask": "",
                "django": "",
                "react": "",
                "java script": "",
                "nodejs": "",
                "Cobol": "",
                "wordpress": "",
                "php": "",
                "redux": "",
                "cordova": "",
                "es6": "",
                "mongodb": "",
                "mysql": "",
                "sass": "",
                "tailwind": "",
                "keycloak": "",
                "Angular 12": "",
                "Bootstrap": "",
                "c#": "",
                "postgresql": "",
                "elastic search": "",
                "kibana": "",
                "apache hadoop": "",
                "azure": "",
                "aws": "",
                "google": "",
                "vba": "",
                "sql": "",
                "windev": "",
                "excel": "",
                "webdesign": "",
                "ajax": "",
                "powerbi": "",
                "rpgle": "",
                "mak": "",
                "mec": "",
                "ssis": "",
                "pbi": "",
                "stream": "",
                "db400": "",
                "anglais": "",
                "typescript": "",
                "angularjs": "",
                "git": "",
                "vuejs": "",
                "nuxtjs": "",
                "c\\+\\+": "",
                "docker": "",
                "network": "",
                "ci/cd": "",
                "golang": "",
                "sass": "",
                "agile": "",
                "scrum": "",
                "kanban": "",
                "dax": "",
                "qlik": "",
                "spark": "",
                "hive": "",
                "presto": "",
                "google analytic": "",
                " r ": "",
            }

            # Nettoyage de la date
            data["clean_date"] = re.findall(r"([0-9]{2}(?=[^0-9]))", data["post_date"])

            if data["clean_date"]:
                data["clean_date"] = int(data["clean_date"][0])
            else:
                data["clean_date"] = ""
            # Minuscules
            data["job_title"] = data["job_title"].lower()

            # Traitement des types de contrat
            "retourne la famille des jobs"
            cdd = re.findall(r"cdd", data["job_title"], re.I)
            cdi = re.findall(r"cdi", data["job_title"], re.I)
            stage = re.findall(r"(stage)|(intern.*)", data["job_title"], re.I)
            alternance = re.findall(r"(altern.*)|(appre.*)", data["job_title"], re.I)
            freelance = re.findall(r"(freelance)|(consultant)", data["job_title"], re.I)

            if cdd:
                data["contract"] = "cdd"
            elif cdi:
                data["contract"] = "cdi"
            elif stage:
                data["contract"] = "stage"
            elif alternance:
                data["contract"] = "alternance"
            elif freelance:
                data["contract"] = "freelance"
            # Traitement des jobs
            "retourne la famille des jobs"
            data_analyst = re.findall(
                r"(data.anal.*)|(donn[ée].*)(visu[ea].*)", data["job_title"], re.I
            )
            data_scientist = re.findall(
                r"(scien.*)| (intelligence)| (miner) ", data["job_title"], re.I
            )
            developpeur = re.findall(
                r"(d[eé]velop.*)|(devop.*)|(web.*)|(program.*)", data["job_title"], re.I
            )
            ingenieur = re.findall(
                r"(engine.*)|(ing[eé]nieur.*)| (engineer.*)",
                data["job_title"],
                re.I,
            )
            business_intelligence = re.findall(
                r"(business.*)|(intel.*)|(bi.*)|(data.intel.*)", data["job_title"], re.I
            )
            manager = re.findall(
                r"(chef.*)|(proje.*)|(mange.*)|(scrum.*)", data["job_title"], re.I
            )
            database = re.findall(
                r"(database.administrat.*)|(administrat.*)|(database.*)",
                data["job_title"],
                re.I,
            )

            if data_analyst:
                data["job_clean"] = "data analyst"
            elif data_scientist:
                data["job_clean"] = "data scientist"
            elif developpeur:
                data["job_clean"] = "developpeur"
            elif business_intelligence:
                data["job_clean"] = "business intelligence"
            elif ingenieur:
                data["job_clean"] = "ingenieur"
            elif manager:
                data["job_clean"] = "manager"
            elif database:
                data["job_clean"] = "database administrator"
            # Expériences
            beginner = re.findall(r"(d[ée]butant)", data["job_title"], re.I)
            junior = re.findall(r"(junior)", data["job_title"], re.I)
            senior = re.findall(r"(senior)", data["job_title"], re.I)

            if beginner:
                data["exp"] = 0
            elif junior:
                data["exp"] = 1
            elif senior:
                data["exp"] = 2
            # Recherche de la présence des différentes compétences, présente : 1 absente : 0
            for i in self.DICTI_TECH:
                if (
                    bool(
                        re.search(
                            "(^.*" + self.DICTI_TECH[i] + ".*$)", str(record[7].split())
                        )
                    )
                    == True
                ):
                    data[self.DICTI_TECH[i]] = 1
                else:
                    data[self.DICTI_TECH[i]] = 0
            # recherche du type de job en télétravail, hybride ou présence si le clean_location est vide
            if (data["clean_location"] == "") == True:
                remote = re.findall(r"t[eéè]l[eéè]travail", record[7])
                if remote:
                    data["remote"] = 1
                    data["clean_location"] = "teletravail"
                else:
                    hybrid = re.findall(r"hybrid|hybride", record[7])
                    if hybrid:
                        data["hybrid"] = 1
                        data["clean_location"] = "hybrid"
                    else:
                        data["presence"] = 1
            # detection du salaire dans le bloc de droite
            # pour les salaires sous la forme 32 - 32 k€
            if (data["salary"] == "") == True:
                if bool(re.findall(r"\d{2} - \d{2} k€", str(record[7]))) == True:
                    salary_right = re.findall(r"\d{2} - \d{2} k€", str(record[7]))
                    salary_split = str(str(salary_right).split())
                    salary_split = salary_split.replace("k€", "")
                    first_sal = int(salary_split[4] + salary_split[5]) * 1000
                    second_sal = int(salary_split[15] + salary_split[16]) * 1000
                    sal = (first_sal + second_sal) / 2
                    sal = round(sal)
                    data["min_salary"] = first_sal
                    data["max_salary"] = second_sal
                    data["annual_salary"] = sal
                    data["monthly_salary"] = round(sal / 12)
                # pour les salaires sour la forme 32 k€
                elif bool(re.findall(r"\d{2} k€", str(record[7]))) == True:
                    salary_right = re.findall(r"\d{2} k€", str(record[7]))
                    salary_split = str(str(salary_right).split())
                    salary_split = salary_split.replace("k€", "")
                    sal = int(salary_split[4] + salary_split[5]) * 1000
                    data["min_salary"] = data["max_salary"] = sal
                    data["annual_salary"] = sal
                    data["monthly_salary"] = round(sal / 12)
                #  pour les salaires sous la forme 1400,00 €, 1400,00€, 1400 € ou 1400€
                else:
                    comment_ = re.sub(r",\d+", "", record[7])
                    salaire = re.findall(
                        r"(\d{1,3} \d{1,3}) €|(\d{1,3} \d{1,3})€|(\d{3,6})€|(\d{3,6}) €",
                        comment_,
                    )
                    # si salaire contient qqch
                    if salaire:
                        z = len(salaire)
                        # et que ça longueur est supérieur à 1
                        if z > 1:
                            first = salaire[0]
                            for i in first:
                                if (i == "") == True:
                                    continue
                                else:
                                    min_sal = i
                                    min_sal = min_sal.replace(" ", "")
                                    min_sal = int(min_sal)
                            second = salaire[1]
                            for i in second:
                                if (i == "") == True:
                                    continue
                                else:
                                    max_sal = i
                                    max_sal = max_sal.replace(" ", "")
                                    max_len = len(max_sal)
                                    max_sal = int(max_sal)
                            #  sal <= 3 permet de vérifier que le chiffre vérifier soit un nombre pouvant correspondre à un salaire mensuelle au minimum
                            if max_len < 3:
                                pass
                            # max_len>4 pour vérifier si c'est un salaire à l'année
                            elif max_len > 4:
                                data["min_salary"] = min_sal
                                data["max_salary"] = max_sal
                                data["annual_salary"] = round(
                                    (data["max_salary"] + data["min_salary"]) / 2
                                )
                            else:
                                data["min_salary"] = min_sal * 12
                                data["max_salary"] = max_sal * 12
                                data["annual_salary"] = round(
                                    (data["max_salary"] + data["min_salary"]) / 2
                                )
                        else:
                            #  répétitiion de la structure précédente
                            first = salaire[0]
                            for i in first:
                                if (i == "") == True:
                                    continue
                                else:
                                    sal = i
                                    sal = sal.replace(" ", "")
                                    sal_len = len(sal)
                                    sal = int(sal)
                            if sal_len < 3:
                                pass
                            elif sal_len > 4:
                                data["min_salary"] = sal
                                data["max_salary"] = sal
                                data["annual_salary"] = data["mean_salary"] = data[
                                    "per_year"
                                ] = round((data["max_salary"] + data["min_salary"]) / 2)
                            else:
                                data["min_salary"] = sal * 12
                                data["max_salary"] = sal * 12
                                data["annual_salary"] = data["mean_salary"] = data[
                                    "per_year"
                                ] = round((data["max_salary"] + data["min_salary"]) / 2)
                    else:
                        data["salary"] = ""
            data = self.cleanRecord(data)

            if self.collec.count_documents({"_id": record[0]}) == 0:
                self.collec.insert_one(data)

    # Nettoyage des enregistrement, partie de Tess
    def cleanRecord(self, data):

        # Traitement sur les salaires
        salary = data["salary"]

        # Si salary est renseigne

        if salary:
            # Temps de travail
            if "par heure" in salary:
                data["interval"] = "per_hour"
            elif "par jour" in salary:
                data["interval"] = "per_day"
            elif "par semaine" in salary:
                data["interval"] = "per_week"
            elif "par mois" in salary:
                data["interval"] = "per_month"
            elif "par an" in salary:
                data["interval"] = "per_year"
            salary = re.sub(r"[a-zA-Z]|[€]|[ ]", "", salary)
            salary = re.sub(r"[,]", ".", salary)

            data["min_salary"] = salary.split("-")[0]
            data["min_salary"] = float(data["min_salary"])  # Convertir en numerique

            if len(salary.split("-")) > 1:

                data["max_salary"] = salary.split("-")[1]
                data["max_salary"] = float(data["max_salary"])  # Convertir en numerique
            else:

                data["max_salary"] = data["min_salary"]
            data["mean_salary"] = statistics.mean(
                [data["min_salary"], data["max_salary"]]
            )
            data["mean_salary"] = round(data["mean_salary"], 2)

            # ],[minimum*1825, minimum*260, minimum*52, minimum*12]
            # Temps de travail
            if data["interval"] == "per_hour":
                data["annual_salary"] = (
                    data["mean_salary"] * 1607
                )  # Heures officielles par an
            elif data["interval"] == "per_day":
                data["annual_salary"] = data["mean_salary"] * 5 * 52
            elif data["interval"] == "per_week":
                data["annual_salary"] = data["mean_salary"] * 52
            elif data["interval"] == "per_month":
                data["annual_salary"] = data["mean_salary"] * 12
            else:
                data["annual_salary"] = data["mean_salary"]
            data["annual_salary"] = round(data["annual_salary"], 2)
        data["clean_location"] = data["job_location"].lower()

        travail_type = data["clean_location"]

        data["clean_location"] = data["clean_location"].split(".")[0]

        if re.findall(r"(france)", data["clean_location"], re.I):
            data["clean_location"] = "france"
            
        data["clean_location"] = data["clean_location"].replace("télétravail", "")
        data["clean_location"] = data["clean_location"].replace("temporaire", "")
        data["clean_location"] = data["clean_location"].replace("hybrid remote", "")
        data["clean_location"] = data["clean_location"].replace("in", "")
        data["clean_location"] = data["clean_location"].split(".")[0]

        data["clean_location"] = re.sub(r"\d+|[)]|[(]|[+]|lieux|lieu", "", data["clean_location"])
        data["clean_location"] = re.sub(r"[éèëê]", "e", data["clean_location"])
        data["clean_location"] = re.sub(r"[àâ]", "a", data["clean_location"])
        data["clean_location"] = re.sub(r"ç", "c", data["clean_location"])
        data["clean_location"] = re.sub(r"ô", "o", data["clean_location"])
        data["clean_location"] = data["clean_location"].strip()
        data['clean_location'] = re.sub(r' [a-z]{1,2}$','', data['clean_location'])

        # data['clean_location'] = data['clean_location'].split(' ')[0]

        remote = re.findall(r"t[eéè]l[eéè]travail", travail_type)
        if remote:
            data["remote"] = 1
        else:
            hybrid = re.findall(r"hybrid|hybride", travail_type)
            if hybrid:
                data["hybrid"] = 1
            else:
                data["presence"] = 1
        return data
