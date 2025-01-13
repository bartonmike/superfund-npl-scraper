# NAME: superfund.py
#
# Python Version Tested With: 3.12.2
#
# 
# Description: This program utilizes the epa superfund site lists through a website and through an xlsx file to create a list of all the sites
#               with their names, states, EPA ID's, and other data along with the cleanup milestones and dates fetched through the cleanup progress
#               section of each individual site.
#
# Requirements: in requirements.txt
#              
# Inputs: URL of EPA Sites Page (Example: https://www.epa.gov/superfund/national-priorities-list-npl-sites-state)
#         XLSX file downloaded from filter search of epa sites on epa website
#
#
# Outputs: CSV file containing data on EPA Sites with Site Name, City, State, EPA ID, Search ID, Score, NAI, NAI Entity, and other dynamically added headers
#

from bs4 import BeautifulSoup # pip3 install beautifulsoup4
import requests # pip3 install requests
from htmldate import find_date #pip3 install htmldate, pip3 install charset_normalizer==2.0.0
from fake_useragent import UserAgent # pip3 install fake_useragent
import csv

import pandas as pd

# bing search imports
from selenium import webdriver # pip3 install selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import os.path

ua = UserAgent()
# creating a fake random useragent
headers = {
    "User-Agent":
    str(ua.chrome)
    }

# initializing selenium chrome tab instance
options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ['enable-logging'])
options.add_argument('--headless=new')
options.add_argument('--log-level=3')
options.add_argument('--no-sandbox')
options.set_capability("browserVersion", "117")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options = options)

counter = 0
# Example of site that code is looking for: https://www.epa.gov/superfund/national-priorities-list-npl-sites-state
url = input("URL of EPA Sites Page: ")

# load url in browser
driver.get(url)

# wait for browser to load content
driver.implicitly_wait(5)

# sees if superfunds.xlsx exists
if(os.path.isfile(os.path.dirname(os.path.abspath(__file__)) + '/superfunds.xlsx')):
    superexists = True
else:
    superexists = False

# if the superfunds.xlsx exists
if(superexists):
    # reads user given xlsx file
    superfunds = pd.read_excel(os.path.dirname(os.path.abspath(__file__)) + '/superfunds.xlsx')

    # find EPA ID, NAI, and NAI Status from xlsx sheet
    id_list = superfunds.get("EPA ID").tolist()
    NA_list = superfunds.get("Native American Interest (NAI)").tolist()
    NA_name_list = superfunds.get("Indian Entity (NAI Status)").tolist()

    header = ['Site Name','City', 'State', 'EPA ID', 'Search ID', 'Score', 'NAI', 'NAI Entity']
else: # different header
    header = ['Site Name','City', 'State', 'EPA ID', 'Search ID', 'Score']

# find names, cities, epaids, links, scores, states, and numbers from the table on epa website
names = driver.find_elements(By.XPATH,"//table/tbody/tr/td[1]")
cities = driver.find_elements(By.XPATH,"//table/tbody/tr/td[2]")
epaids = driver.find_elements(By.XPATH,"//table/tbody/tr/td[3]")
l = driver.find_elements(By.XPATH,"//table/tbody/tr/td[7]/ul/li[2]/a")
scores = driver.find_elements(By.XPATH,"//table/tbody/tr/td[5]")
states = driver.find_elements(By.XPATH,"//table/thead/tr/th/span[1]")
number = driver.find_elements(By.XPATH,"//table/thead/tr/th/span[2]")

sites  = []

# goes through all states headers harvested from website "( # sites )" and strips the number, adding text version of that state that many times into array
for i in range(len(states)):
    for p in range(int(number[i].text.replace('(','').replace(" sites )",'').replace(" site )",''))):
        sites.append(str(states[i].text))


data = []

# for every site
for i in range(len(l)):
    print("Current Header: " + str(header))
    try:
        print("Name: " + str(names[i].text))

        # add NAI if the xlsx file exists
        if(superexists):
            
            # initializing NAI
            NAI_status = 'N/A'
            NAI_entity = ''

            # for each entry in the xlsx list, try to find an EPA ID match with the online table
            # if there is a match, transfer NAI entity and status data
            for j in range(len(id_list)):
                if id_list[j].lower() in (epaids[i].text).lower():
                    NAI_status = NA_list[j]
                    NAI_entity = NA_name_list[j]
                    id_list.pop(j)
                    NA_list.pop(j)
                    NA_name_list.pop(j)
                    if NAI_status == 'No':
                        NAI_entity = ''
                    break

            print("NAI?: " + str(NAI_status))
            print("NAI Entity: " + str(NAI_entity) + '\n')
            
            # create entry to populate in csv file
            # ['Site Name','City', 'State', 'EPA ID', 'Search ID', 'Score', 'NAI', 'NAI Entity']
            entry = [names[i].text, cities[i].text, sites[i], epaids[i].text, l[i].get_attribute('href')[-7:], scores[i].text, NAI_status, NAI_entity]
        else:
            entry = [names[i].text, cities[i].text, sites[i], epaids[i].text, l[i].get_attribute('href')[-7:], scores[i].text]
        
        # add empty values to entry corresponding to the dynamically added columns from the milestone data
        if len(entry) < len(header):
            for i in range((len(header) - len(entry))):
                entry.append('')

        # using search id, go to cleanup progress
        link = 'https://cumulis.epa.gov/supercpad/SiteProfiles/index.cfm?fuseaction=second.schedule&id=' + entry[4]

        # get text and data from link
        p = requests.get(link, headers = headers)
        soup = BeautifulSoup(p.text, features = "html.parser")
        milestones = []
        dates = []
        
        # get table from cleanup progress, get all milestones and dates
        for row in soup.findAll('table')[0].tbody.findAll('tr'):
            milestones.append(str(row.findAll('td')[0].contents[0]))
            dates.append(str(row.findAll('td')[1].contents[0]))


        # start after the initialized data of the entry
        if(superexists):
            constant = 8
        else:
            constant = 6

        # for the length of milestones in the cleanup table
        for num in range(len(milestones)):

            found = False
            # for each dynamic header in current csv entries
            for i in range(len(header) - constant):
                # try to match milestone header to current headers
                if milestones[num] in header[i + constant]:
                    comma = ''
                    # if it was already populated, there must be duplicate entries, different dates
                    if entry[i + constant] != '':
                        comma = ', '
                    # add date of milestone to entry
                    entry[i + constant] += comma + dates[num]
                    found = True
                    break
            
            # if there was no match with the milestone
            if(found == False):
                print('added "' + milestones[num] + '" in position ' + str(num + constant))
                # create a new column into entry and add milestone
                header.insert(num + constant, milestones[num])
                entry.insert(num + constant, dates[num])
                # update previous entries in data so that column exists and is empty
                for item in data:
                    item.insert(num + constant, '')
        
        # append new entry
        data.append(entry)
        counter += 1
        print("\nNumber: " + str(counter))
        print("Entry: " + str(entry))
    except Exception as e:
        
        # if there is an index out of range error, there is most likely no table that was found, therefore update entry accordingly
        if "list index out of range" in str(e):
            message = entry + ["can't find table"]
            print("Number: " + str(counter))
            print(message)
            data.append(entry + ["can't find table"])
            counter += 1
        else: # if other error, then append entry and continue with program
            message = entry + ["error making entry"]
            print("Number: " + str(counter))
            print(message)
            data.append(entry + ["error making entry"])
            counter += 1

# creating csv file, adding the headers and all the data/articles
print("----Writing CSV......")
with open("superfund.csv", 'w', encoding="utf-8") as file:
    csvwriter = csv.writer(file) # 2. create a csvwriter object
    csvwriter.writerow(header) # 4. write the header
    csvwriter.writerows(data) # 5. write the rest of the data
print("Done")
driver.close()
