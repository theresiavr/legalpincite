import pandas as pd

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

import time
import logging

import os

folder = "citation_page_source"

df = pd.read_csv('raw/search_result_20260523.csv', #search result file obtained from EUR-Lex
                 on_bad_lines='warn', 
                 usecols=["CELEX number", "Title", "Date of document"])

df = df.drop_duplicates()

list_celex = df["CELEX number"].tolist()

# create directories
if not os.path.exists(folder):
    os.makedirs(folder)

if not os.path.exists('log'):
    os.makedirs('log')


log_file_name = 'log/retrieve_citation.log'


# logging config
logging.basicConfig(
    filename=log_file_name,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


# Chrome options
chrome_options = Options()
chrome_options.add_argument("--start-maximized")

# Launch browser
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=chrome_options
)

for celex in list_celex:

    url = f"https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX:{celex}"

    try:
        # Open page
        driver.get(url)

        # Wait for JS rendering
        time.sleep(5)

        html = driver.page_source

        with open(f'{folder}/{celex}.html', 'w', encoding='utf-8') as f:
            print(html, file=f)

        logging.info(f"Successfully retrieved page source for CELEX {celex}")

    except:
        logging.error(f"Error occurred while retrieving citation for CELEX: {celex}")

driver.quit()