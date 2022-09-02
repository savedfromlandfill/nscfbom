#
# bom.py
# Read bom.gov.au files from free anon ftp
# brm 26/08/2022
#

# IMPORTS

from ftplib import FTP
from bs4 import BeautifulSoup, Tag
import datetime
import os

# SETTINGS

# bom ftp server address
bom_ftp = 'ftp.bom.gov.au' 

# path to forecast, warning and observation products
bom_dir = 'anon/gen/fwo' 

# File details at  
bom_forecast = 'IDQ10095.txt' # IDQ10095  City Forecast - Brisbane (QLD)
bom_river = 'IDQ60005.html'   # IDQ60005  River Height Bulletin - All Queensland Rivers (QLD)
bom_rain = 'IDQ60348.html'    # IDQ60348  3 Hour Rainfall Bulletin - Brisbane, Bremer (QLD)

river_stations = ['Ithaca Ck at Jason St Ithaca *','Enoggera Ck at Bancroft Pk K Grove#',
                  'Breakfast Ck at Bowen Hills Rail #','Enoggera Reservoir #',
                  'Enoggera Reservoir *','Brisbane R at City Gauge #']
rainfall_stations = ['Mt Coot-Tha AL *','Mt Nebo AL *']

print("*** bom.py started ***")

print("checking file date/times.")
if os.path.exists(bom_forecast) and os.path.exists(bom_river) and os.path.exists(bom_rain):
    forecast_time = os.path.getmtime(bom_forecast)
    river_time = os.path.getmtime(bom_river)
    rain_time = os.path.getmtime(bom_rain)
    print(datetime.datetime.fromtimestamp(forecast_time))


# open ftp connection
ftp = FTP(bom_ftp)
ftp.login()
ftp.cwd(bom_dir) # change working directory
print("ftp connected.")

# download files
print("downloading forecast: "+bom_forecast)
with open(bom_forecast, 'wb') as fp:
    ftp.retrbinary('RETR ' + bom_forecast, fp.write)
fp.close()

print("downloading river heights: "+bom_river)
with open(bom_river, 'wb') as fp:
    ftp.retrbinary('RETR ' + bom_river, fp.write)
fp.close()

print("downloading rainfall: "+bom_rain)
with open(bom_rain, 'wb') as fp:
    ftp.retrbinary('RETR ' + bom_rain, fp.write)
fp.close()

ftp.quit()
print("ftp closed.")

print("processing results:")
with open(bom_river) as fp:
    soup = BeautifulSoup(fp, "html.parser")

# process heights
table = soup.find("table", {"class": "tabledata rhb"})

heights = {}
for tr in table.find_all("tr"):
    tds = tr.find_all("td")

    # ignore table headers
    if len(tds) == 0: 
        continue

    station_name = tds[0].text.strip()
    height = tds[2].text.strip()

    if station_name in river_stations:
        heights[station_name] = height

print(heights)

# process rainfall
with open(bom_rain) as fp:
    soup = BeautifulSoup(fp, "html.parser")

tables = soup.find_all("table")

rainfall = {}
for table in tables:
    for tr in table.find_all("tr"):
        tds = tr.find_all("td")

        # ignore table headers
        if len(tds) == 0: 
            continue

        rstation_name = tds[0].text.strip().replace("\u00a0", " ") # replace non-breaking space with space
        if rstation_name in rainfall_stations:
            rainfall[rstation_name] = tds[8].text.strip()

print(rainfall)

#
# TODO
#
# 1) process downloaded files using beautifulsoup library for html and 'regular expression' searches for txt.
# 2) create dashboard and format output based on triggers.
# 3) send sms/email alerts based on triggers.
# 4) find somewhere to host this program and run at specified intervals.
#

#
# TRIGGERS
#
# 1st Level Trigger/s: - a BOM forecast of a high chance of 100mm or more of rainfall in Brisbane and/or its hinterland over one or two days. 
#
# 2nd Level Trigger/s: - reports of 100mm or more of rain on Mt Cootha and/or Mt Nebo, and/or 
#                      - the water level rising rapidly at the Bancroft Park gauge towards the 4m level.
#
# 3rd Level Trigger/s: - water level at the Bancroft Park gauge continuing to rise above 4m.
#