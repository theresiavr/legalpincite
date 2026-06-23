import logging
import os

from bs4 import BeautifulSoup
import glob

import json
from tqdm import tqdm

# create directories
if not os.path.exists('raw_citation_data'):
    os.makedirs('raw_citation_data')

log_file_name = 'log/extract_all_citation.log'

# logging config
logging.basicConfig(
    filename=log_file_name,
    level=logging.INFO,  
    format='%(asctime)s - %(levelname)s - %(message)s'
)

list_file = glob.glob("citation_page_source/*")


# Extract any types of citations
citation_dict = dict()

for file in tqdm(list_file):
    celex = os.path.split(file)[-1]\
                                .replace(".html", "")

    with open(file, "rb") as f:
        html = f.read()

    soup = BeautifulSoup(html,'html.parser')

    for el in soup.find_all("dt"):
        if "Instruments cited" in el.text:
            break
    else:
        logging.warning(f"Could not find the section of 'Instruments cited' for {celex}")
        continue

    dd_content = el.find_next("dd")

    each_bullet_point = dd_content\
                                .find("ul")\
                                .find_all("li")
    
    list_citation = []

    for x in each_bullet_point:
        text = x.get_text()
        clean_text = text.strip("\n")
        list_citation.append(clean_text) 

    citation_dict[celex] = list_citation

with open("raw_citation_data/all_citation.json", "w", encoding='utf-8') as f:
    json.dump(citation_dict, f, indent=4)

logging.info(f"Finish extracting citation for {len(citation_dict)} documents")