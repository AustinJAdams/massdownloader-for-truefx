#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
from clint.textui import progress
from zipfile import ZipFile
import os
import datetime
import argparse

#This could be useful if I implement this better
# currencies = ",".join(['AUDJPY', 'AUDNZD', 'AUDUSD', 'CADJPY', 'CHFJPY', 'EURCHF', 'EURGBP',
#                 'EURJPY', 'EURUSD', 'GBPJPY', 'GBPUSD', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY'])
# months = ",".join(["{:02d}".format(x) for x in range(1, 13)])
# years = ",".join([str(y) for y in range(2009, datetime.datetime.today().year + 1)])
# path = "{}/".format(os.getcwd())   

parser = argparse.ArgumentParser(description="Add your TrueFX username and password.", epilog='Written by Austin Adams')
parser.add_argument("username", help="Your Truefx username")
parser.add_argument("password", help="Your Truefx password")
args = parser.parse_args()

months = []
year_adj = ''
name_to_number = {}
test_val = ""
for i in range(1,13):
    months.append(datetime.date(2008, i, 1).strftime('%B').lower())
for i in range(1,13):
    if len(str(i)) == 1:
        year_adj = "0" + str(i)
    else:
        year_adj = i
    name_to_number[str(datetime.date(2008, i, 1).strftime('%B').lower())] = year_adj
    
payload = {'USERNAME': str(args.username), 'PASSWORD': str(args.password)}
url = 'https://www.truefx.com/?page=downloads'
with requests.Session() as session:
    #First, we authenticate with the server login page
    session.post('https://www.truefx.com/?page=loginz', data=payload)
    
    #We then navigate to the URL link
    response = session.get(url)
    html = BeautifulSoup(response.content, 'html.parser')
    
    #This initializes the list of all href links in the HTML to then parse
    href = []
    for year in html.find_all('a'):
        
        #If this breaks, go update the string that follows the html of the site
        #We look for this string, which gives us the specific download links
        if str(year.get('href'))[0:31] == '?page=download&description=year':
            href.append(str(year.get('href')))


    #Now that we have all the hrfs of the download links, we iterate over that list and enter it
    for year in href:
        down_page_year = 'https://www.truefx.com/{}'.format(year)
        response_next_year = session.get(down_page_year)
        response_next_year = BeautifulSoup(response_next_year.content, 'html.parser')
        
        #The last four digits are always the year value
        year_val = year[-4:]
        href2 = []

        #In all the month page hrefs, we look to see if there is a month in any of the hrefs
        for month in response_next_year.find_all('a'):
            if any(month_val in month.get('href') for month_val in months):
                href2.append(month.get('href'))
        
        #Create the underlying directory to then enter
        os.mkdir('data/{}'.format(year_val))

        #Now we iterate over the month hrefs
        for month in href2:
            down_page_month = 'https://www.truefx.com/{}'.format(month)
            response_next_month = session.get(down_page_month)
            response_next_month = BeautifulSoup(response_next_month.content, 'html.parser')
            
            #There are two different styles TrueFX used
            year_month = month.split('/')[-1][-7:]
            year_month = year_month.split("-")
            #One has a string first (the month), and the other has the year
            try:
                test_val = int(year_month[0])
                year_month = year_month[0] + "-" + year_month[1] 
            except:
                year_val[0] = name_to_number[year_month[0].lower()]
                year_month = year_month[1] + "-" + year_month[0]
            print(year_month)
            os.mkdir('data/{}/{}'.format(year_val, year_month))

            #Now we look for the download links by searching for zips
            for pair in response_next_month.find_all('a'):
                url_string = pair.get('href')
                
                if '.zip' in url_string:
                    #we now are at the end, so we query the download and save it
                    url_val = url_string.split('/')[-1]
                    print(url_val)
                    down_page_pair = 'https://www.truefx.com/{}'.format(url_string)
                    data = requests.get(down_page_pair, stream = True)
                    url_val = url_string.split('/')[-1]
                    print('data/{}/{}/{}'.format(year_val, year_month, url_val))

                    #We use chunk-size saving to then save the data 
                    #Thanks to https://github.com/Sebastiaan76/truefx-downloader for this part
                    with open('data/{}/{}/{}'.format(year_val, year_month, url_val), 'wb') as f:
                        total_length = int(data.headers.get('content-length'))
                        for chunk in progress.bar(data.iter_content(chunk_size=1024), expected_size=(total_length / 1024) + 1):
                            if chunk:
                                f.write(chunk)
                                f.flush()
                    print("{} is done.".format(url_val))

                    #We then open the zip file, unzip it, then delete the zip
                    with ZipFile('data/{}/{}/{}'.format(year_val, year_month, url_val), 'r') as zip:
                        
                        print('Extracting all the files now...')
                        zip.extractall('data/{}/{}'.format(year_val, year_month))
                        print('Done')
                        os.remove('data/{}/{}/{}'.format(year_val, year_month, url_val))
                        print("deleted zip file: {}".format(url_val))