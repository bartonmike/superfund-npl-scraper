# NAME: superfund.py
#
# Python Version Tested With: 3.12.2
#
# 
# Description: This program utilizes the epa superfund site lists through an xlsx file to create a list of all the sites
#               with their names, states, EPA ID's, and other data along with the cleanup milestones and dates fetched through the cleanup progress
#               section of each individual site.
#
# Requirements: in requirements.txt
#              
# Input: XLSX file downloaded from filter search of epa sites on epa website
#
#
# Outputs: CSV file containing data on EPA Sites with Site Name, City, State, EPA ID, Search ID, Score, NAI, NAI Entity, NPL Status, and other dynamically added headers
#


from bs4 import BeautifulSoup # pip3 install beautifulsoup4
import requests # pip3 install requests
from htmldate import find_date #pip3 install htmldate, pip3 install charset_normalizer==2.0.0
from fake_useragent import UserAgent # pip3 install fake_useragent
import csv
import os

import pandas as pd

ua = UserAgent()
# creating a fake random useragent
headers = {
    "User-Agent":
    str(ua.chrome)
    }

counter = 0

# reads user given xlsx file
superfunds = pd.read_excel(os.path.dirname(os.path.abspath(__file__)) + '/superfunds.xlsx')

# find EPA ID, NAI, and NAI Status from xlsx sheet
id_list = superfunds.get("EPA ID").tolist()
NA_list = superfunds.get("Native American Interest (NAI)").tolist()
NA_name_list = superfunds.get("Indian Entity (NAI Status)").tolist()
names = superfunds.get("Site Name").tolist()
cities = superfunds.get("City").tolist()
l = len(superfunds)
scores = superfunds.get("HRS Score").tolist()
states = superfunds.get("State").tolist()
links = superfunds.get("Superfund Site Profile Page URL").tolist()
status = superfunds.get("NPL Status").tolist()

header = ['Site Name','City', 'State', 'EPA ID', 'Search ID', 'Score', 'NAI', 'NAI Entity', 'NPL Status', 'Community Advisory Group?']
data = []

# for every site
for i in range(l):
    # current xlsx file header
    print("Current Header: " + str(header))
    try:
        # list name and NAI of current entry
        print("Name: " + str(names[i]))
        print("NAI?: " + str(NA_list[i]))
        print("NAI Entity: " + str(NA_name_list[i]) + '\n')

        # use link provided to access site
        p = requests.get("https://" + links[i], headers = headers)
        milestones = []
        dates = []

        # new link is redirect, get search id at end
        link = p.url[-7:]

        # using search id, go to cleanup progress
        p = requests.get('https://cumulis.epa.gov/supercpad/SiteProfiles/index.cfm?fuseaction=second.schedule&id=' + link, headers=headers)
        soup = BeautifulSoup(p.text, features = "html.parser")

        # using search id, go to Stady Updated, Get Involved
        pl = requests.get('https://cumulis.epa.gov/supercpad/SiteProfiles/index.cfm?fuseaction=second.Stayup&id=' + link, headers=headers)
        soupl = BeautifulSoup(pl.text, features = "html.parser")

        if "Community Advisory Group" in str(soupl):
            advisory = "Yes"
        else:
            advisory = "No"
        
        # get table from cleanup progress, get all milestones and dates
        for row in soup.findAll('table')[0].tbody.findAll('tr'):
            milestones.append(str(row.findAll('td')[0].contents[0]))
            dates.append(str(row.findAll('td')[1].contents[0]))

        # create entry to populate in csv file
        # ['Site Name','City', 'State', 'EPA ID', 'Search ID', 'Score', 'NAI', 'NAI Entity', 'NPL Status']
        entry = [names[i], cities[i], states[i], id_list[i], p.url[-7:], scores[i], NA_list[i], NA_name_list[i], status[i], advisory]
        
        # add empty values to entry corresponding to the dynamically added columns from the milestone data
        if len(entry) < len(header):
            for i in range((len(header) - len(entry))):
                entry.append('')

        # start after the initialized data of the entry
        constant = 10

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
        print("Number: " + str(counter))
        print("Entry: " + str(entry))
    except Exception as e:

        # if there is an index out of range error, there is most likely no table that was found, therefore update entry accordingly
        if "list index out of range" in str(e):
            message = entry + ["can't find table"]
            print("Number: " + str(counter))
            print(message)
            data.append(entry + ["can't find table"])
            counter += 1
        else:# if other error, then stop and create csv
            print(str(e))

            data.append([names[i], cities[i], states[i], id_list[i], '', scores[i], NA_list[i], NA_name_list[i], status[i], ''] + ["can't find table"])
            # creating csv file, adding the headers and all the data/articles
            # print("----Writing CSV......")
            # with open("superfund_xlsx.csv", 'w', encoding="utf-8") as file:
            #     csvwriter = csv.writer(file) # 2. create a csvwriter object
            #     csvwriter.writerow(header) # 4. write the header
            #     csvwriter.writerows(data) # 5. write the rest of the data
            # print("Done")
            # exit()

# creating csv file, adding the headers and all the data/articles
print("----Writing CSV......")
with open("superfund_xlsx.csv", 'w', encoding="utf-8") as file:
    csvwriter = csv.writer(file) # 2. create a csvwriter object
    csvwriter.writerow(header) # 4. write the header
    csvwriter.writerows(data) # 5. write the rest of the data
print("Done")
