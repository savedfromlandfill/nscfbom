# nscfbom.py
# Read bom.gov.au files from free anon ftp
# brm 26/08/2022
#
# TRIGGERS
# 1st Level Trigger/s: - a BOM forecast of a high chance of 100mm or more of rainfall in Brisbane and/or its hinterland over one or two days.
#
# 2nd Level Trigger/s: - reports of 100mm or more of rain on Mt Cootha and/or Mt Nebo, and/or
#                      - the water level rising rapidly at the Bancroft Park gauge towards the 4m level.
#
# 3rd Level Trigger/s: - water level at the Bancroft Park gauge continuing to rise above 4m.
#

from bs4 import BeautifulSoup, Tag
from collections import OrderedDict
from datetime import datetime
import logging
import os
from pathlib import Path
import re
import time
import xml.etree.ElementTree as ET

from brm import brm_email
from brm import brm_ftp

# working from the same directory as this script
os.chdir(os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(
    filename = "nscf_bom.log",
    encoding = "utf-8",
    format = "%(asctime)s %(levelname)-8s %(message)s",
    level = logging.INFO,
    datefmt = "%Y-%m-%d %H:%M:%S",
)

BOM_FTP_URL = "ftp.bom.gov.au"
BOM_FTP_PATH = "anon/gen/fwo" # path to forecast, warning and observation products
BOM_FORECAST = "IDQ10095.xml" # IDQ10095  City Forecast - Brisbane (QLD)
BOM_RIVER_HEIGHTS = "IDQ60005.html" # IDQ60005  River Height Bulletin - All Queensland Rivers (QLD)
BOM_RAINFALL = "IDQ60348.html" # IDQ60348  3 Hour Rainfall Bulletin - Brisbane, Bremer (QLD)

RIVER_HEIGHTS_STATIONS = [
    "Breakfast Ck at Bowen Hills Rail #",
    "Brisbane R at City Gauge #",
    "Enoggera Ck at Bancroft Pk K Grove#",
    "Enoggera Reservoir #",
    "Enoggera Reservoir *",
    "Ithaca Ck at Jason St Ithaca *"
]

RAINFALL_STATIONS = ["Mt Coot-Tha AL *", "Mt Nebo AL *"]

ADMIN_EMAILS = ["ben.mcalister+nscfbom@gmail.com"]
ADMIN_TOUCHFILE = os.path.join(os.getcwd(), "nscfbom.admin")

ALERT_EMAILS = ["ben.mcalister+nscfbom@gmail.com"]
ALERT_TOUCHFILE = os.path.join(os.getcwd(), "nscfbom.alert")

DAILY_EMAILS = ["ben.mcalister+nscfbom@gmail.com"]
DAILY_TOUCHFILE = os.path.join(os.getcwd(), "nscfbom.daily")

TRIGGER_FORECAST_MM = 100
TRIGGER_RAINFALL_MM = 100
TRIGGER_HEIGHT_M = 3.0

TIME_NOW = time.time()
NOW_STR = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
TIME_24H_AGO = TIME_NOW - 60 * 60 * 24
TIME_8H_AGO = TIME_NOW - 60 * 60 * 8
TIME_4H_AGO = TIME_NOW - 60 * 60 * 4

admin_text = ""
alert_text = ""
daily_text = ""


print("***** nscfbom.py started " + NOW_STR + " *****")
print("current path: " + os.getcwd())

logging.info("***** nscfbom.py started *****")


#brm_ftp.ftp_download(BOM_FTP_URL, BOM_FTP_PATH, {BOM_FORECAST, BOM_RIVER_HEIGHTS, BOM_RAINFALL})


# Process river heights file
logging.info("checking river heights.")

with open(os.path.join(os.getcwd(), BOM_RIVER_HEIGHTS)) as fp:
    soup = BeautifulSoup(fp, "html.parser")

table = soup.find("table", {"class": "tabledata rhb"})

heights = {}
for tr in table.find_all("tr"):
    tds = tr.find_all("td")

    # ignore table headers
    if len(tds) == 0:
        continue

    station_name = tds[0].text.strip()
    height = tds[2].text.strip()

    if station_name in RIVER_HEIGHTS_STATIONS:
        heights[station_name] = height

print("river heights: ", heights)
daily_text = daily_text + "River/Creek Heights:\r"
heights_ordered = OrderedDict(sorted(heights.items()))
for creek in heights_ordered:
    daily_text = daily_text + "  " + creek + ": " + heights_ordered[creek] + "\r"


# Process rainfall file
logging.info("checking rainfall.")

with open(os.path.join(os.getcwd(), BOM_RAINFALL)) as fp:
    soup = BeautifulSoup(fp, "html.parser")

tables = soup.find_all("table")

rainfall = {}
for table in tables:
    for tr in table.find_all("tr"):
        tds = tr.find_all("td")

        # ignore table headers
        if len(tds) == 0:
            continue

        # replace non-breaking space with space
        rain_station_name = (tds[0].text.strip().replace("\u00a0", " "))

        if rain_station_name in RAINFALL_STATIONS:
            rainfall[rain_station_name] = tds[8].text.strip()

print("rainfall: ", rainfall)
daily_text = daily_text + "\rRainfall Current:\r"

for rainloc in rainfall:
    daily_text = daily_text + "  " + rainloc + ": " + rainfall[rainloc] + "\r"


# Process forecast file
logging.info("checking forecast.")
tree = ET.parse(os.path.join(os.getcwd(), BOM_FORECAST))
root = tree.getroot()
daily_text = daily_text + "\rForecast Rainfall for Brisbane:\r"

for fcp in root.findall(
    ".//*[@description='Brisbane'][@type='location']/forecast-period"
):
    for child in fcp:
        if child.attrib["type"] == "precipitation_range":
            print(
                fcp.get("start-time-local").split("T")[0],
                child.attrib["type"],
                child.text,
            )
            forecast_date = datetime.strptime(
                fcp.get("start-time-local").split("T")[0], "%Y-%m-%d"
            )
            daily_text = (
                daily_text
                + "  "
                + datetime.strftime(forecast_date, "%A, %d %B %Y").replace(", 0", ", ")
                + ": "
                + child.text
                + "\r"
            )
            for mm in re.findall(r"\d+\.*\d*", child.text):
                if float(mm) >= TRIGGER_FORECAST_MM:
                    alert_text = (
                        alert_text + "Brisbane rainfall forecast of " + mm + "mm.\r"
                    )

daily_text = (
    daily_text
    + "\r\rNote: This is just a regular daily report. "
    + "Additional messages will be sent if alerts are triggered."
)


# Send emails
if alert_text != "" and (
    not os.path.exists(ALERT_TOUCHFILE) or os.path.getctime(ALERT_TOUCHFILE) < TIME_4H
):
    Path(ALERT_TOUCHFILE).touch()
    logging.info("sending ALERT emails!")
    brm_email.send_email(ALERT_EMAILS, "NSCF BOM Weather Alert!", alert_text)

if admin_text != "" and (
    not os.path.exists(ADMIN_TOUCHFILE) or os.path.getctime(ADMIN_TOUCHFILE) < TIME_8H_AGO
):
    Path(ADMIN_TOUCHFILE).touch()
    logging.info("sending admin emails.")
    brm_email.send_email(ADMIN_EMAILS, "NSCFBOM.PY Admin Notice", admin_text)

if daily_text != "" and (
    not os.path.exists(DAILY_TOUCHFILE) or os.path.getctime(DAILY_TOUCHFILE) < TIME_24H_AGO + 60 * 10
):
    Path(DAILY_TOUCHFILE).touch()
    logging.info("sending daily emails.")
    brm_email.send_email(
        DAILY_EMAILS,
        "NSCF Daily Weather Report",
        NOW_STR + "\r\r" + daily_text + "\rSent by the nscfbom.py script " + NOW_STR,
    )


logging.info("finished running.")
