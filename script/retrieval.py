import pyterrier as pt
import pandas as pd

import os
import time

from pyterrier.measures import *

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

data_path = "https://huggingface.co/datasets/theresiavr/legalpincite/resolve/main"

list_metrics = [
                "num_q", "num_ret", "num_rel", "num_rel_ret",
                Success@3, Success@5, Success@10,
                nDCG@3, nDCG@5, nDCG@10,
                "recip_rank",
                AP,
                ] 

def set_up_pt():
    java_home = "C:/Program Files/Java/jdk-25.0.2" # ensure java installed and change path accordingly
    pt.java.set_java_home(java_home)


def load_data(split, query_level, doc_level):
    queries = pd.read_csv(f"{data_path}/query_{split}_{query_level}.csv")
    qrel = pd.read_csv(f"{data_path}/qrel_{split}_{query_level}_{doc_level}.csv")
    return queries, qrel


def main(exp_name, split, query, doc):
    print(f"Starting experiment {exp_name, split, query, doc}")

    save_path = f"experiment/{exp_name}"

    if not os.path.exists(save_path):
        os.makedirs(save_path)

    set_up_pt()

    queries, qrel = load_data(split, query, doc)

    if n_sample>0:
        test_queries = queries.head(n_sample)
    else:
        test_queries = queries

    index = pt.Artifact.from_hf(f'theresiavr/legalpincite_doc_{split}_{doc}.terrier')

    # if you have download the index locally, use this line instead: 
    # index = pt.terrier.TerrierIndex(f"{path}/doc_{split}_{doc}.terrier/")

    tfidf = index.tf_idf()
    bm25 = index.bm25()
    dirichlet_lm = index.dirichlet_lm()
    dph = index.dph()

    start_time = time.time()
    res = pt.Experiment(
        [tfidf, bm25, dirichlet_lm, dph],
        test_queries,
        qrel,
        names=["TF-IDF", "BM25", "LMIR", "DPH"],
        eval_metrics=list_metrics,
        perquery="both",
        save_dir=save_path,
        filter_by_qrels=True #this changes the default behaviour; only intersection between test_queries and qrel are used to evaluate
    )

    end_time = time.time()

    time_taken = end_time-start_time
    print(f"Time taken for {exp_name} is {time_taken} seconds")

    res.averages.to_csv(f"experiment/aggregate_result_{exp_name}.csv")
    res.perquery.to_csv(f"experiment/perquery_result_{exp_name}.csv")

if __name__ == '__main__':
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("-n", "--n_sample", default=-1, type=int, help="How many queries; -1 means all queries are used")
    parser.add_argument("-s", "--split", type=str)
    parser.add_argument("-q", "--query", type=str)
    parser.add_argument("-d", "--doc", type=str)
    parser.add_argument("-e", "--experiment_name_suffix", default="", type=str, help="Suffix name needs to include _")
    args = vars(parser.parse_args())

    # Set up parameters
    n_sample = args["n_sample"]
    split = args["split"]
    query = args["query"]
    doc = args["doc"]
    suffix = args["experiment_name_suffix"]

    # === FOR DEBUGGING ===
    # n_sample = 10
    # split = "dev"
    # query = "par"
    # doc = "par"

    exp_name = f"{split}_{query}_{doc}"

    if suffix != "":
        exp_name += suffix

    main(exp_name, split, query, doc)
