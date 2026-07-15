import numpy as np
import pyterrier as pt
import pandas as pd

import json

import os
import time
import logging

from pyterrier.measures import *

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

log = logging.getLogger(__name__)

n_sample = -1  # means all queries are used
data_path = "https://huggingface.co/datasets/theresiavr/legalpincite/resolve/main"


list_metrics = [
                "num_q", "num_ret", "num_rel", "num_rel_ret",
                Success@3, Success@5, Success@10,
                nDCG@3, nDCG@5, nDCG@10,
                "recip_rank",
                AP,
                ]


def set_up_pt():
    java_home = "C:\Program Files\Java\jdk-25.0.2"
    pt.java.set_java_home(java_home)


def load_data(split, query_level, doc_level):
    queries = pd.read_csv(f"{data_path}/query_{split}_{query_level}.csv")
    qrel = pd.read_csv(f"{data_path}/qrel_{split}_{query_level}_{doc_level}.csv")
    return queries, qrel


def get_best_params(tuned_model, param_dict):
    model_param_dict = param_dict.values()
    assert len(model_param_dict) == 1

    param_keys = list(model_param_dict)[0].keys()

    best_params = {}

    for param_name in param_keys:
        new_param_name = param_name\
                                .split(".")[-1]\
                                .replace("_", "")
        best_params[new_param_name] = tuned_model.controls[param_name]

    return best_params


def main(exp_name, query, doc):
    log.info(f"Starting experiment {exp_name, query, doc}")

    save_path = f"tuning/{exp_name}"

    for split in ["dev", "test"]:
        if not os.path.exists(save_path+"_"+split):
            os.makedirs(save_path+"_"+split)

    set_up_pt()

    dev_queries, dev_qrel = load_data("dev", query, doc)
    test_queries, test_qrel = load_data("test", query, doc)

    filter_by_qrels = False

    if n_sample > 0:
        dev_queries = dev_queries.head(n_sample)
        test_queries = test_queries.head(n_sample)
        filter_by_qrels = True

    index = pt.Artifact.from_hf(f'theresiavr/legalpincite_doc_dev_{doc}.terrier')

    # if you have downloaded the index locally, use this line instead:
    # index = pt.terrier.TerrierIndex(f"{path}/doc_dev_{doc}.terrier/")

    tfidf = index.tf_idf()
    bm25 = index.bm25()
    dirichlet_lm = index.dirichlet_lm()
    dph = index.dph()

    param_map_tfidf = {
        tfidf: {
            "tf_idf.b": np.arange(0, 1.1, 0.25),
            "tf_idf.k_1": np.arange(0, 3.1, 0.75)
            },
    }

    param_map_bm25 = {
        bm25: {
            "bm25.b": np.arange(0, 1.1, 0.25),
            "bm25.k_1": np.arange(0, 3.1, 0.75),
            },
    }

    param_map_dirichlet_lm = {
        dirichlet_lm: {
            "dirichletlm.mu": [100, 500, 800, 1000, 2000, 4000, 8000, 10000]
        }
    }

    eval_args = dict(
                    topics=dev_queries,
                    qrels=dev_qrel,
                    metric="ndcg_cut_10",
                )

    start_time = time.time()

    log.info("Starting tuning for TF-IDF")

    tfidf_tuned = pt.GridSearch(
                            tfidf,
                            param_map_tfidf,
                            **eval_args
                        )

    log.info("Starting tuning for BM25")

    bm25_tuned = pt.GridSearch(
                            bm25,
                            param_map_bm25,
                            **eval_args
                        )

    log.info("Starting tuning for Dirichlet LM")

    dlm_tuned = pt.GridSearch(
                            dirichlet_lm,
                            param_map_dirichlet_lm,
                            **eval_args
                        )

    tfidf_param = get_best_params(tfidf_tuned, param_map_tfidf)
    bm25_param = get_best_params(bm25_tuned, param_map_bm25)
    dlm_param = get_best_params(dlm_tuned, param_map_dirichlet_lm)

    # save best parameters as json
    best_params = {
        "TF-IDF": tfidf_param,
        "BM25": bm25_param,
        "Dirichlet LM": dlm_param,
    }

    with open(save_path+"_dev/best_param.json", "w") as f:
        json.dump(best_params, f)

    log.info("Start evaluation on dev")

    dev_res = pt.Experiment(
        [tfidf_tuned, bm25_tuned, dlm_tuned, dph],
        dev_queries,
        dev_qrel,
        names=["TF-IDF", "BM25", "LMIR", "DPH"],
        eval_metrics=list_metrics,
        filter_by_qrels=filter_by_qrels,
        perquery="both",
        save_dir=save_path+"_dev",
    )

    log.info("Start evaluation on test")

    index = pt.Artifact.from_hf(f'theresiavr/legalpincite_doc_test_{doc}.terrier')

    # if you have downloaded the index locally, use this line instead:
    # index = pt.terrier.TerrierIndex(f"{path}/doc_test_{doc}.terrier/")

    for_eval_tfidf = index.tf_idf(**tfidf_param)
    for_eval_bm25 = index.bm25(**bm25_param)
    for_eval_dirichlet_lm = index.dirichlet_lm(**dlm_param)
    for_eval_dph = index.dph()

    res = pt.Experiment(
        [for_eval_tfidf, for_eval_bm25, for_eval_dirichlet_lm, for_eval_dph],
        test_queries,
        test_qrel,
        names=["TF-IDF", "BM25", "LMIR", "DPH"],
        eval_metrics=list_metrics,
        filter_by_qrels=filter_by_qrels,
        perquery=False,  # only do average
        save_dir=save_path+"_test",
    )

    end_time = time.time()

    time_taken = end_time-start_time

    log.info(f"Time taken for {exp_name} is {time_taken} seconds")

    # save results
    dev_res.averages.to_csv(f"tuning/result_dev_{query}_{doc}_aggregate.csv")
    dev_res.perquery.to_csv(f"tuning/result_dev_{query}_{doc}_perquery.csv")

    res.to_csv(f"tuning/result_test_{query}_{doc}_aggregate.csv")


if __name__ == '__main__':

    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("-n", "--n_sample", default=-1, type=int, help="How many queries; -1 means all queries are used")
    parser.add_argument("-q", "--query", type=str)
    parser.add_argument("-d", "--doc", type=str)
    args = vars(parser.parse_args())

    # Set up parameters
    n_sample = args["n_sample"]
    query = args["query"]
    doc = args["doc"]

    # === FOR DEBUGGING ===
    # n_sample = 10
    # split = "dev"
    # query = "par"
    # doc = "par"

    exp_name = f"{query}_{doc}"
    main(exp_name, query, doc)
