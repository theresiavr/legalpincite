import pandas as pd

import json
import logging


log_file_name = 'log/extract_cj_par_citation.log'

# logging config
logging.basicConfig(
    filename=log_file_name,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

with open("raw_citation_data/all_citation.json", "r") as f:
    citation_dict = json.load(f)

# Extract only citation to specific paragraphs of case law (CJ): 
df_par2par = pd.DataFrame(columns=["CELEX_FROM", "NUMBER_FROM", "CELEX_TO", "NUMBER_TO"])

for citing_doc_no, citation_line in citation_dict.items():

    # Example: 61970CJ0011-N3: N 77
    # meaning 61970CJ0011, par 3 is cited in par 77 of the citing document

    for cited_doc in citation_line:

        # citation to CJ (case law)
        if "CJ" not in cited_doc:
            continue
        
        if ": " not in cited_doc:
            logging.warning(f"No information on citing paragraph numbers for '{cited_doc}' in {citing_doc_no}")
            continue

        if cited_doc.count(": ") > 1:
            logging.warning(f"Multiple ': ' in '{cited_doc}' in {citing_doc_no}, which may lead to wrong parsing. Skipping")
            continue
        
        cited_doc_par, citing_par = cited_doc.split(": ")

        # citation to specific number
        if "-N" not in cited_doc_par:
            continue
        
        cited_doc_no, cited_par_no = cited_doc_par.split("-N")

        citing_par_no = citing_par\
                                .replace("N ","")\
                                .split(" ")

        # handle multiple citing paragraph
        if "-" in citing_par_no:
            logging.warning(f"Multiple citing paragraphs for {citing_doc_no} citing {cited_doc_no} in {citing_par}")
                    
            idx_hyphen = citing_par_no.index("-")

            num_before_hyphen = int(citing_par_no[idx_hyphen-1])
            num_after_hyphen = int(citing_par_no[idx_hyphen+1])

            for num in range(num_before_hyphen+1, num_after_hyphen):
                citing_par_no.append(str(num))

            citing_par_no.remove("-")

            logging.info(f"After handling hyphen, citing_par_no is {citing_par_no}")
        
        df_to_add = pd.DataFrame([{
                                    "CELEX_FROM": citing_doc_no,
                                    "NUMBER_FROM": citing_par_no,
                                    "CELEX_TO": cited_doc_no,
                                    "NUMBER_TO": cited_par_no
                                    }])

        df_to_add = df_to_add.explode("NUMBER_FROM")

        df_par2par = pd.concat([df_par2par, df_to_add], ignore_index=True)

df_par2par[["NUMBER_FROM", "NUMBER_TO"]] = df_par2par[["NUMBER_FROM", "NUMBER_TO"]].astype(int)
df_par2par = df_par2par.sort_values(by=["CELEX_FROM", "NUMBER_FROM", "CELEX_TO", "NUMBER_TO"])

df_par2par.to_csv("raw_citation_data/cj_par2par_citation.csv", index=False)

logging.info(f"Finish extracting {len(df_par2par)} CJ-par citations")