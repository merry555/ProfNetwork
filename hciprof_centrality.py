import pandas as pd
import glob
import networkx as nx
import matplotlib.pyplot as plt
import collections
import sys
import re

def return_centralities_as_dict(input_g):
    def return_weighted_degree_centrality(input_g, normalized=False):
        w_d_centrality = {n:0.0 for n in input_g.nodes()}
        for u, v, d in input_g.edges(data=True):
            w_d_centrality[u]+=d['weight']
            w_d_centrality[v]+=d['weight']
        if normalized==True:
            weighted_sum = sum(w_d_centrality.values())
            return {k:v/weighted_sum for k, v in w_d_centrality.items()}
        else:
            return w_d_centrality
    def return_closeness_centrality(input_g):
        new_g_with_distance = input_g.copy()
        for u,v,d in new_g_with_distance.edges(data=True):
            if 'distance' not in d:
                d['distance'] = 1.0/d['weight']
        return nx.closeness_centrality(new_g_with_distance, distance='distance')
    def return_betweenness_centrality(input_g):
        return nx.betweenness_centrality(input_g, weight='weight')
    def return_pagerank(input_g):
        return nx.pagerank(input_g, weight='weight')
    return {
        # 'weighted_deg':return_weighted_degree_centrality(input_g),
        # 'closeness_cent':return_closeness_centrality(input_g), 
        # 'betweeness_cent':return_betweenness_centrality(input_g),
        'pagerank':return_pagerank(input_g)
    }


def find(counter, ids):
    ids = list(ids)
    status = False
    for number in range(len(counter)):
        list_int = list(map(int, counter[number][0]))
        status = (sorted(ids) == sorted(list_int))

        if status is True:
            return counter[number]

def matrix():
    frame = pd.read_excel('./{publication_information}.xlsx', index_col=None, engine='openpyxl') # input publication information file
    frame = frame.drop_duplicates()
    frame = frame.reset_index()

    author_ids = []

    for i in range(len(frame)):
        author_ids.append(frame['Scopus Author Ids'][i].replace(' ','').split('|'))

    author_ids_m = sum(author_ids, [])
    author_ids_m = set(author_ids_m)
    print("authors : %s",len(author_ids_m))

    data = []
    words = []

    for i in range(len(author_ids)):
        c = nx.complete_graph(author_ids[i])
        edges = c.edges()
        data.append(list(edges))

    for i in range(len(author_ids)):
        for j in range(len(data[i])):
            words.append(data[i][j])

    counter=list(collections.Counter(words).items())

    print("========================= STEP1 : finish make counter ===========================")

    ids = pd.read_csv('hci_scopus_ids.csv')

    # 243만 추리기
    df = pd.DataFrame(columns=ids['scopus id'], index=ids['scopus id'])
    df = df.fillna(0)

    c = nx.complete_graph(df)
    edges = c.edges()
    ids_hci = list(edges)

    data_list = []

    for i in range(len(ids_hci)):
        print(i)
        data_list.append(find(list(counter), ids_hci[i]))
    op_arr = list(filter(None,data_list))
    print("========================= STEP2 : finish ===========================")

    G = nx.Graph()

    for i in range(len(op_arr)):
        G.add_weighted_edges_from(
            [
                (list(op_arr[i][0])[0], list(op_arr[i][0])[1], float(op_arr[i][1]))
            ]
        )
    
    print("========================= STEP2 : finish ===========================")

    return G

def get_centrality():
    G = matrix()

    key = []
    value = []
        
    for k, v in return_centralities_as_dict(G).items():
        a = str(v)
    a = a.replace(a[0],'').replace(a[len(a)-1],'').replace(' ','')
    a = a.split(',')

    for i in range(len(a)):
        key.append(a[i].split(':')[0])
        value.append(a[i].split(':')[1])

    result = pd.DataFrame({'Scopus ID':key, 'value':value})
    result.to_csv("./{centrality_results}.csv", mode='w') # input centrality results name

if __name__ =='__main__':
    get_centrality()