
# 👩‍⚖️ LegalPincite - Dataset for Multi-level Legal Retrieval

LegalPincite is a large-scale legal information retrieval dataset for citation-oriented retrieval based on Court of Justice of the European Union (CJEU) judgments from [EUR-Lex](https://eur-lex.europa.eu/homepage.html). It supports retrieval at multiple levels of granularity:

| Retrieval setting | Query | Candidate document | Typical task |
| --- | --- | --- | --- |
| **Case-to-case** | Full citing case | Candidate case | Retrieve cases relevant to a case. |
| **Paragraph-to-case** | Citing paragraph | Candidate case | Retrieve cases relevant to a specific legal paragraph. |
| **Paragraph-to-paragraph** | Citing paragraph | Candidate paragraph | Retrieve relevant legal paragraph (legal pincite). |

This repository contains code that provides both simple examples and full experimental pipeline, including:

- loading the dataset
- loading the provided PyTerrier indexes (or re-creating them)
- performing simple retrieval
- running sparse retrieval baselines, with and without hyperparameter tuning
- applying semantic reranking with MonoT5 and LegalBERT (additional examples not included in the paper)
- retrieval/reranking evaluation

More information about the dataset (e.g., query, corpus, qrel statistics), can be found on the HuggingFace Hub dataset page and in the accompanying dataset paper:

- Dataset: <https://huggingface.co/datasets/theresiavr/legalpincite>
- Paper: <https://arxiv.org/abs/2608.03756>

We also provide the raw citation data (prior to temporal-based splitting and filtering to train, dev, and test) in the `raw_citation_data` folder and the code to scrape/extract them from EUR-Lex in the `scraper` folder.

## Repository Contents

```text
.
|-- README.MD
|-- LICENSE
|-- example.ipynb
|-- raw_citation_data/
|   |-- all_citation.json
|   `-- cj_par2par_citation.csv
|-- scraper/
|   |-- extract_all_citation.py
|   |-- extract_cj_par_citation.py
|   `-- get_citation.py
|-- script/
    |-- retrieval.py
    |-- retrieval_small.sh
    |-- retrieval.sh
    |-- tuning.py
    `-- tuning.sh
`-- tuning/
```

- `example.ipynb`: end-to-end examples for loading LegalPincite, running retrieval, reranking results with cross-encoder (MonoT5) and bi-encoder (LegalBERT).
- `raw_citation_data/all_citation.json`: all unparsed citation data (raw citation strings) from CJEU judgments available in English, with date of documents from 2021--2025; keys are the citing CELEX number and values are the cited CELEX number (not necessarily a CJEU judgment)
- `raw_citation_data/cj_par2par_citation.csv`: parsed 41,551 CJEU paragraph-to-paragraph citations (41,547 unique) with citing and cited CELEX/paragraph numbers; only from CJEU judgments available in English with date of documents from 2021--2025;
- `scraper/get_citation.py`: downloads EUR-Lex HTML page containing "Instruments cited" for CELEX IDs from a search-result CSV.
- `scraper/extract_all_citation.py`: extracts raw citation strings from saved EUR-Lex HTML pages.
- `scraper/extract_cj_par_citation.py`: converts raw citation strings and filters into the CJEU paragraph-to-paragraph citation CSV.
- `script/retrieval.py`: baseline retrieval with TF-IDF, BM25, LMIR, and DPH.
- `script/retrieval_small.sh`: small smoke test using five queries for paragraph-to-paragraph retrieval (on the dev split).
- `script/retrieval.sh`: full baseline runs for dev/test and all supported query-document levels.
- `script/tuning.py`: tunes hyperparameters of baseline retrievers with grid search on the dev split and evaluates the best configurations on test split; contains hyperparameter search space.
- `script/tuning.sh`: performs tuning and testing for all supported query-document levels.
- `tuning/`: reports hyperparameter configurations with the best NDCG@10 on dev split.

## Setup

Install Conda or Miniconda first if it is not already available: <https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html>.

Create and activate a Python environment:

```bash
conda create -n legalpincite
conda activate legalpincite
```

Install the Python dependencies used by the examples:

```bash
pip install -r requirements.txt
```

Some notes:

- PyTerrier requires Java. Before running `script/retrieval.py`, update the `java_home` value in that file to match your Java installation location.

- An internet connection is required because the scripts load CSV files and Terrier indexes from Hugging Face.

## Run Retrieval Baselines (No Tuning)

First activate the environment:

```bash
conda activate legalpincite
```

Run a small smoke test:

```bash
bash script/retrieval_small.sh
```

This runs `dev/par/par` retrieval on five queries and will write:

- `experiment/aggregate_result_dev_par_par_small.csv`
- `experiment/perquery_result_dev_par_par_small.csv`

If everything went well, run the full baseline set used by the dataset experiments:

```bash
bash script/retrieval.sh
```

The full script runs TF-IDF, BM25, LMIR, and DPH over these combinations:

| Split | Query level | Document level |
| --- | --- | --- |
| `dev` | `par` | `par` |
| `dev` | `par` | `case` |
| `dev` | `case` | `case` |
| `test` | `par` | `par` |
| `test` | `par` | `case` |
| `test` | `case` | `case` |

You can also run one experiment directly:

```bash
python script/retrieval.py -s dev -q par -d par
```

Useful options:

```bash
python script/retrieval.py -s dev -q par -d par -n 5 -e _small
```

- `-s`, `--split`: `dev` or `test`
- `-q`, `--query`: `par` or `case`
- `-d`, `--doc`: `par` or `case` (note that `par` here should not be used with `case` on query)
- `-n`, `--n_sample`: number of queries to run; `-1` uses all queries
- `-e`, `--experiment_name_suffix`: suffix added to the output experiment name

## Run Retrieval Baselines (With Tuning)

```bash
bash script/tuning.sh
```

This will automatically tune the hyperparameters of each baseline retriever on the dev split for all valid query-document level pairs, save the best configuration, and use it for testing.

## Run Scraper Pipeline

We provide the code that we used to extract citations from EUR-Lex. This step is not necessary for running the retrieval baselines above.
The first step expects a EUR-Lex search-result CSV at `raw/search_result_20260523.csv` with the columns `CELEX number`, `Title`, and `Date of document`.

`scraper/get_citation.py` uses Selenium with Chrome. Chrome installation may be required. If these scraper dependencies are not already installed in your environment, install them first:

```bash
pip install selenium webdriver-manager
```

Preferably with a stable internet connection, download the EUR-Lex pages, extract all citation strings, and then extract the CJEU paragraph-to-paragraph citations:

```bash
python scraper/get_citation.py
python scraper/extract_all_citation.py
python scraper/extract_cj_par_citation.py
```

The scraper pipeline writes saved HTML pages to `citation_page_source/`, logs to `log/`, raw citation strings to `raw_citation_data/all_citation.json`, and parsed CJEU paragraph-to-paragraph citations to `raw_citation_data/cj_par2par_citation.csv`.

## License

The code in this repository is released under the MIT License. The LegalPincite dataset on Hugging Face and the raw citation data in this repository are released under CC BY 4.0.

## Citation

If you use LegalPincite, please cite the dataset DOI, the accompanying paper, and the papers of the original datasets. If you use the raw citation data or the the code in the `scraper` folder, please cite the accompanying dataset paper.

### Dataset Citation

```bibtex
@dataset{rampisela_legalpincite_2026,
  title        = {LegalPincite: Multi-level Legal Information Retrieval Dataset},
  author       = {Rampisela, Theresia Veronika and Olsen, Henrik Palmer and Colavizza, Giovanni},
  year         = {2026},
  publisher    = {Hugging Face},
  doi          = {10.57967/hf/9072},
  url          = {https://huggingface.co/datasets/theresiavr/legalpincite},
  license      = {CC-BY-4.0}
}
```

### Paper Citation

#### Accompanying dataset paper

```bibtex
@misc{rampisela2026legalpincite,
      title={LegalPincite: Multi-level Legal Information Retrieval Dataset}, 
      author={Theresia Veronika Rampisela and Henrik Palmer Olsen and Giovanni Colavizza},
      year={2026},
      eprint={2608.03756},
      archivePrefix={arXiv},
      primaryClass={cs.IR},
      url={https://arxiv.org/abs/2608.03756}, 
}
```

#### Papers of the original datasets

- Henrik Palmer Olsen, Nicolas Garneau, Yannis Panagis, and Johan Lindholm. 2026. Providing legal pincite recommendations using language representations. *Artificial Intelligence and Law* (2026). <doi:10.1007/s10506-025-09493-3>
- Henrik Palmer Olsen, Nicolas Garneau, Yannis Panagis, Johan Lindholm, and Anders Søgaard. 2023. Re-Framing Case Law Citation Prediction from a Paragraph Perspective. In *Legal Knowledge and Information Systems - JURIX 2023 (Frontiers in Artificial Intelligence and Applications).* Giovanni Sileno, Jerry Spanakis, and Gijs van Dijck (Eds.). IOS Press BV, Netherlands, 323–328. <doi:10.3233/FAIA230982>

```bibtex
@inproceedings{Olsen2023ReFraming,
  title = "Re-Framing Case Law Citation Prediction from a Paragraph Perspective",
  author = "Olsen, {Henrik Palmer} and Nicolas Garneau and Yannis Panagis and Johan Lindholm and Anders S{\o}gaard",
  year = "2023",
  doi = "10.3233/FAIA230982",
  series = "Frontiers in Artificial Intelligence and Applications",
  publisher = "IOS Press BV",
  pages = "323--328",
  editor = "Giovanni Sileno and Jerry Spanakis and {van Dijck}, Gijs",
  booktitle = "Legal Knowledge and Information Systems - JURIX 2023",
  address = "Netherlands",
}

@article{Olsen2026ProvidingPincite,
  title = "Providing legal pincite recommendations using language representations",
  author = "Olsen, {Henrik Palmer} and Nicolas Garneau and Yannis Panagis and Johan Lindholm",
  year = "2026",
  doi = "10.1007/s10506-025-09493-3",
  journal = "Artificial Intelligence and Law",
  issn = "0924-8463",
  publisher = "Springer Nature",
}
```
