#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
from tqdm import tqdm
import xmltodict, json
import time
import urllib
import re


# # Requêtes courtes 

# In[5]:


i = 0
similarity_list = ["advanced_TFIDF", "advanced_BM25", "advanced_LMDirichlet", "advanced_LMJ", "advanced_SweetSpot",                    "baseline_TFIDF", "baseline_BM25", "baseline_LMDirichlet", "baseline_LMJ", "baseline_SweetSpot"]
for similarity in similarity_list: 
    i = i + 1
    print("Processing similarity {} of {} ({})..".format(i, len(similarity_list), similarity))
    core_name = 'NLP_' + similarity
    outputFile = 'requete_courtes_' + similarity + '.txt'
    f = open(outputFile, 'w')
    queryFile = open('queries.txt')
    queries = queryFile.readlines();
    qId = ''
    qText = ''
    IRModel='STANDARD'
    for q in tqdm(queries):
        q = q.replace("  ", " ")
        if q.strip().startswith("<num>"):
            num = str(int(q.split(" ")[2].strip())) 
        if q.strip().startswith("<title>"):
            title = q.split(" ", 2)[2]
            title = title.replace(" ", "%20")
            title = title.replace("\n", "") 
            inurl = 'http://localhost:8983/solr/'+core_name+'/select?q=%27'+title+'%27&fl=DOCNO%2Cscore&wt=json&indent=true&rows=1000'
            data = urllib.request.urlopen(inurl)
            docs = json.load(data)['response']['docs']
            rank = 1
            for doc in docs:
                f.write(num + ' ' + 'Q0' + ' ' + doc['DOCNO'].strip() + ' ' + str(rank) + ' ' + str(doc['score']) + ' ' + IRModel + '\n')
                rank += 1
    f.close()
    queryFile.close()
    print('SUCCESS!')


# # Requetes longues

# In[4]:


## Reqêtes longues ##
i = 0
similarity_list = ["advanced_TFIDF", "advanced_BM25", "advanced_LMDirichlet", "advanced_LMJ", "advanced_SweetSpot",                    "baseline_TFIDF", "baseline_BM25", "baseline_LMDirichlet", "baseline_LMJ", "baseline_SweetSpot"]
for similarity in similarity_list: 
    i = i + 1
    print("Processing similarity {} of {} ({})..".format(i, len(similarity_list), similarity))
    core_name = 'NLP_' + similarity
    outputFile = 'requete_longues_' + similarity + '.txt'
    f = open(outputFile, 'w')
    queryFile = open('queries.txt')
    queries = queryFile.readlines();
    qId = ''
    qText = ''
    #IRModel='DFR'
    IRModel='STANDARD'

    queries_string = " ".join(queries)
    queries_string = queries_string.replace("\n", " ")
    for q in tqdm(queries):
        q.replace('\nDocument', ' Document')
        queries_string = queries_string.removeprefix(q.strip().replace("\n", ""))
        queries_string = queries_string.lstrip()
        q = q.replace("  ", " ")
        
        if q.strip().startswith("<num>"):
            num = str(int(q.split(" ")[2].strip()))

        if q.strip().startswith("<title>"):
            title = q.split(" ", 2)[2]
            title = title.replace(" ", "%20")
            title = title.replace("\n", "") 

        if q.strip().startswith("<desc>"):
            desc = re.match('.*?Document.*?<narr>', queries_string).group().replace("<narr>", "").rstrip().replace("<desc> Description:", "").lstrip()
            desc = " ".join(desc.split()[3:]) # remove the first 3 words
            desc = desc.replace(" ", "%20") # HTML encoding for correct request with inurl
            inurl = 'http://localhost:8983/solr/'+core_name+'/select?q=%27'+title+'%20'+desc+'%27&fl=DOCNO%2Cscore&wt=json&indent=true&rows=1000'
            data = urllib.request.urlopen(inurl)
            docs = json.load(data)['response']['docs']
            rank = 1
            for doc in docs:
                f.write(num + ' ' + 'Q0' + ' ' + doc['DOCNO'].strip() + ' ' + str(rank) + ' ' + str(doc['score']) + ' ' + IRModel + '\n')
                rank += 1
    f.close()
    queryFile.close()
    print("SUCCESS!")


# In[ ]:




