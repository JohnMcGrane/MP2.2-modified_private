import math
import sys
import time
import metapy
import pytoml


def load_ranker(cfg_file):
    """
    Use this function to return the Ranker object to evaluate,
    The parameter to this function, cfg_file, is the path to a
    configuration file used to load the index.
    """

    # return metapy.index.OkapiBM25(k1=1.01, b=1, k3=1.1)
    # return metapy.index.AbsoluteDiscount(0.68)
    # 0.3632004003860273  0.4126221963338141 NEED 0.4171734094008867
    return metapy.index.OkapiBM25(k1=2.054, b=0.779, k3=0.0001)
    #                                                                                0.4122144465864736
    #                                                                                0.4126221963338141
    # return metapy.index.JelinekMercer(1.45)
    # return metapy.index.PivotedLength(0.35)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: {} config.toml".format(sys.argv[0]))
        sys.exit(1)

    cfg = sys.argv[1]
    print('Building or loading index...')
    idx = metapy.index.make_inverted_index(cfg)
    ranker = load_ranker(cfg)
    ev = metapy.index.IREval(cfg)

    with open(cfg, 'r') as fin:
        cfg_d = pytoml.load(fin)

    query_cfg = cfg_d['query-runner']
    if query_cfg is None:
        print("query-runner table needed in {}".format(cfg))
        sys.exit(1)

    start_time = time.time()
    top_k = 10
    query_path = query_cfg.get('query-path', 'queries.txt')
    query_start = query_cfg.get('query-id-start', 0)

    query = metapy.index.Document()
    ndcg = 0.0
    num_queries = 0

    print('Running queries')
    with open(query_path) as query_file:
        for query_num, line in enumerate(query_file):
            query.content(line.strip())
            results = ranker.score(idx, query, top_k)
            ndcg += ev.ndcg(results, query_start + query_num, top_k)
            num_queries += 1
    ndcg = ndcg / num_queries

    print("NDCG@{}: {}".format(top_k, ndcg))
    print("Elapsed: {} seconds".format(round(time.time() - start_time, 4)))
