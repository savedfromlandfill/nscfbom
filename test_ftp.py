import os
import pickle

from brm import brm_ftp

# working from the same directory as this script
os.chdir(os.path.dirname(os.path.abspath(__file__)))

BOM_FTP_URL = "ftp.bom.gov.au"
BOM_FTP_PATH = "anon/gen/fwo" # path to forecast, warning and observation products
BOM_FTP_FORECAST = "IDQ10095.xml" # IDQ10095  City Forecast - Brisbane (QLD)
BOM_FTP_RIVER_HEIGHTS = "IDQ60005.html" # IDQ60005  River Height Bulletin - All Queensland Rivers (QLD)
BOM_FTP_RAINFALL = "IDQ60348.html" # IDQ60348  3 Hour Rainfall Bulletin - Brisbane, Bremer (QLD)


# brm_ftp.ftp_download(BOM_FTP_URL, BOM_FTP_PATH, {BOM_FTP_FORECAST, BOM_FTP_RIVER_HEIGHTS, BOM_FTP_RAINFALL})

brm_ftp.ftp_listdates(BOM_FTP_URL, BOM_FTP_PATH, {BOM_FTP_FORECAST, BOM_FTP_RIVER_HEIGHTS, BOM_FTP_RAINFALL})
