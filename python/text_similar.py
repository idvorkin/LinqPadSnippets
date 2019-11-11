import os
from pyrxnlp.api.cluster_sentences import ClusterSentences


# replace this with your api key (see: http://www.rxnlp.com/api-key/)
# apikey =

# Cluster from a list of sentences

path = "~/gits/igor2/grateful_summary.txt"
fp = open(os.path.expanduser(path))
list_of_sentences = fp.readlines()

# initialize sentence clustering

clustering = ClusterSentences(apikey)

# generate clusters and print

clusters = clustering.cluster_from_list(list_of_sentences)

if clusters is not None:

    print("------------------------------")
    print("Clusters from a list of sentences")
    print("------------------------------")
    clustering.print_clusters(clusters)
    print(clusters)
