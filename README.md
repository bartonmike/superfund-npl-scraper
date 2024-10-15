# superfund-npl-scraper
A Python scraper that can pull data related to the superfund national priority list (both current and archived)
There are two versions of this scraper, 
  one utilizes an online table of the current superfund national priority list sites and an XLSX file containing results from a search of SNP results on the EPA site.
  Another only uses the XLSX file of SNP results on the EPA Site

## What It Does
This program scans given data, through an XLSX file and/or site data, about various superfund sites and takes the site name, city, EPA ID, Search ID, Score, NAI, and NAI Entity 
In addition to these headers, the program goes to each site's EPA profile and takes the milestone and date data from the cleanup progress table. Since the milestones are varied, when the program encounters a new milestone it dynamically adds it to the table, thus different sites could yield different milestones on the table. 
After the program is finished, it creates a CSV (excel/sheets) file named "superfunds.csv" or "superfunds_xlsx.csv" that outputs the data that it found. 

## Program Requirements
All Python requirements for the program are contained in the requirements.txt file
before running the program type this command and press enter into the command line:
```
pip install -r requirements.txt
```
After installing requirements, make sure that the XLSX file is in the same directory and named "superfunds.xlsx" before running the program

## How to acquire XLSX file
Go to this page on the advanced search of superfund sites: https://cumulis.epa.gov/supercpad/cursites/srchsites.cfm
filter for desired sites and click search at the bottom
once the website has searched and returned results, click the link "Download Excel file containing values for all search criteria" 
rename the XLSX file to "superfunds.xlsx" and put it into the same directory as requirements.txt and superfund.py

## Differences between XLSX only version and Site/XLSX version
### Site/XLSX
The Site/XLSX version enables the ability to pull data completely online instead of an XLSX file, although it does still need the XLSX file for the NAI status and NAI Entity, but if those are not needed
the program can operate with only site data given the site. 
An example of the format of the online spl site is as follows: https://www.epa.gov/superfund/national-priorities-list-npl-sites-state
This program also assumes that the NPL site status is given, as there are different NPL site lists for each status (deleted/ongoing)

### XLSX
This program creates the CSV file completely based on the XLSX file, it also has an additional column detailing the "NPL Status" such as deleted, proposed, ongoing, etc.
Unlike the Site/XLSX version, it does not need an additional website to run, but this means that a new XLSX file needs to be downloaded to create a new updated CSV file.

## Running the program
make sure that the program (superfund.py) and the XLSX file (superfunds.xlsx) 
go to the same directory as the program in the command line
run the program by typing in this command 
```
python superfund.py
```
answer the prompt for the site link if you chose the Site/XLSX version
