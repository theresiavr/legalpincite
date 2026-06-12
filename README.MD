
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
- running sparse retrieval baselines (code for experiments presented in the paper)
- applying semantic reranking with MonoT5 and LegalBERT (additional examples not included in the paper)
- retrieval/reranking evaluation

More information about the dataset (e.g., query, corpus, qrel statistics), can be found on the HuggingFace Hub dataset page and in the accompanying dataset paper:

- Dataset: <https://huggingface.co/datasets/theresiavr/legalpincite>
- Paper: TBA

## Repository Contents

```text
.
|-- README.MD
|-- LICENSE
|-- example.ipynb
`-- script/
    |-- retrieval.py
    |-- retrieval_small.sh
    `-- retrieval.sh
```

- `example.ipynb`: end-to-end examples for loading LegalPincite, running retrieval, reranking results with cross-encoder (MonoT5) and bi-encoder (LegalBERT).
- `script/retrieval.py`: baseline retrieval with TF-IDF, BM25, LMIR, and DPH (results are in the paper).
- `script/retrieval_small.sh`: small smoke test using five queries for paragraph-to-paragraph retrieval (on the dev split).
- `script/retrieval.sh`: full baseline runs for dev/test and all supported query-document levels.

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

## Run Retrieval Baselines

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

## License

The code in this repository is released under the MIT License. The LegalPincite dataset on Hugging Face is released under CC BY 4.0.

## Citation

If you use LegalPincite, please cite the dataset DOI, the accompanying paper (TBA), and the papers of the original datasets.

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

TBA

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
