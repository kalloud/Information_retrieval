#!/usr/bin/env python
# coding: utf-8

# # Evaluation du système RI

# In[1]:


import os
from tqdm import tqdm
import xmltodict, json
import time
import urllib
import re


# In[21]:


## Requêtes courtes ##
i = 0
similarity_list = ["advanced_TFIDF", "advanced_BM25", "advanced_LMDirichlet", "advanced_LMJ", "advanced_SweetSpot",                    "baseline_TFIDF", "baseline_BM25", "baseline_LMDdirichlet", "baseline_LMJ", "baseline_SweetSpot"]
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


# In[24]:


## Reqêtes longues ##
i = 0
similarity_list = ["advanced_TFIDF", "advanced_BM25", "advanced_LMDirichlet", "advanced_LMJ", "advanced_SweetSpot",                    "baseline_TFIDF", "baseline_BM25", "baseline_LMDdirichlet", "baseline_LMJ", "baseline_SweetSpot"]
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


# In[26]:


inurl


# # BASELINE APPROACH

# ### Requêtes courtes (champ "title" seulement)

# In[3]:


core_name = 'NLP_baseline'
#core_name = 'NLP_advanced'
outputFile = 'requete_courtes_baseline_results.txt'
f = open(outputFile, 'w')
queryFile = open('queries.txt')
queries = queryFile.readlines();
qId = ''
qText = ''
#IRModel='DFR'
IRModel='STANDARD'
for q in tqdm(queries):
    q = q.replace("  ", " ")
    # deal with the document number qID
    if q.strip().startswith("<num>"):
        num = str(int(q.split(" ")[2].strip())) 
    if q.strip().startswith("<title>"):
        title = q.split(" ", 2)[2]
        title = title.replace(" ", "%20")
        title = title.replace("\n", "") 
       #inurl = 'http://localhost:8983/solr/NLP_project/select?q='+title+'&fl=id%2Cscore&wt=json&indent=true&rows=20&qf=text_en^1.1%20text_de^1.1%20text_ru^0.3&defType=dismax'
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


# ### Requêtes longues (champs "title" et "desc")

# In[4]:


outputFile = 'requete_longues_baseline_results.txt'
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
    # input("Press any key to continue")
    q.replace('\nDocument', ' Document')
    #print("q is:                       ", q)
    #print("queries_string starts with: ", queries_string[:80])
    queries_string = queries_string.removeprefix(q.strip().replace("\n", ""))
    queries_string = queries_string.lstrip()
    #print("removing prefix..")
    #print("queries_string starts with: ", queries_string[:80])
    
    q = q.replace("  ", " ")
    # deal with the document number qID
    if q.strip().startswith("<num>"):
        num = str(int(q.split(" ")[2].strip()))
        
    if q.strip().startswith("<title>"):
        title = q.split(" ", 2)[2]
        title = title.replace(" ", "%20")
        title = title.replace("\n", "") 

    if q.strip().startswith("<desc>"):
        desc = re.match('.*?Document.*?<narr>', queries_string).group().replace("<narr>", "").rstrip().replace("<desc> Description:", "").lstrip()
        desc = " ".join(desc.split()[3:]) # remove the first 3 words
        #print("desc contains:              ", desc)
        desc = desc.replace(" ", "%20") # HTML encoding for correct request with inurl
       #inurl = 'http://localhost:8983/solr/NLP_project/select?q='+title+'&fl=id%2Cscore&wt=json&indent=true&rows=20&qf=text_en^1.1%20text_de^1.1%20text_ru^0.3&defType=dismax'
        inurl = 'http://localhost:8983/solr/'+core_name+'/select?q=%27'+title+'%20'+desc+'%27&fl=DOCNO%2Cscore&wt=json&indent=true&rows=1000'
        data = urllib.request.urlopen(inurl)
        docs = json.load(data)['response']['docs']
        rank = 1
        for doc in docs:
           #f.write(num + ' ' + 'Q0' + ' ' + str(doc['DOCNO']) + ' ' + str(rank) + ' ' + str(doc['score']) + ' ' + IRModel + '\n')
            f.write(num + ' ' + 'Q0' + ' ' + doc['DOCNO'].strip() + ' ' + str(rank) + ' ' + str(doc['score']) + ' ' + IRModel + '\n')
           #query_id, iter, docno, rank, sim, run_id
            rank += 1

f.close()
queryFile.close()
print("SUCCESS!")


# # ADVANCED APPROACH

# ### Requêtes courtes (champ "title" seulement)

# In[6]:


#core_name = 'NLP_baseline'
core_name = 'NLP_advanced'

outputFile = 'requete_courtes_advanced_results.txt'
f = open(outputFile, 'w')
queryFile = open('queries.txt')
queries = queryFile.readlines();
qId = ''
qText = ''
#IRModel='DFR'
IRModel='STANDARD'
for q in tqdm(queries):
    q = q.replace("  ", " ")
    # deal with the document number qID
    if q.strip().startswith("<num>"):
        num = str(int(q.split(" ")[2].strip())) 
    if q.strip().startswith("<title>"):
        title = q.split(" ", 2)[2]
        title = title.replace(" ", "%20")
        title = title.replace("\n", "") 
       #inurl = 'http://localhost:8983/solr/NLP_project/select?q='+title+'&fl=id%2Cscore&wt=json&indent=true&rows=20&qf=text_en^1.1%20text_de^1.1%20text_ru^0.3&defType=dismax'
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


# ### Requêtes longues (champs "title" et "desc")

# In[8]:


outputFile = 'requete_longues_advanced_results.txt'
f = open(outputFile, 'w')
queryFile = open('queries.txt')
queries = queryFile.readlines();
qId = ''
qText = ''
#IRModel='DFR'
IRModel='STANDARD'

core_name = 'NLP_advanced'
#core_name = 'NLP_baseline'
queries_string = " ".join(queries)
queries_string = queries_string.replace("\n", " ")
for q in tqdm(queries):
    # input("Press any key to continue")
    q.replace('\nDocument', ' Document')
    #print("q is:                       ", q)
    #print("queries_string starts with: ", queries_string[:80])
    queries_string = queries_string.removeprefix(q.strip().replace("\n", ""))
    queries_string = queries_string.lstrip()
    #print("removing prefix..")
    #print("queries_string starts with: ", queries_string[:80])
    
    q = q.replace("  ", " ")
    # deal with the document number qID
    if q.strip().startswith("<num>"):
        num = str(int(q.split(" ")[2].strip()))
        
    if q.strip().startswith("<title>"):
        title = q.split(" ", 2)[2]
        title = title.replace(" ", "%20")
        title = title.replace("\n", "") 

    if q.strip().startswith("<desc>"):
        desc = re.match('.*?Document.*?<narr>', queries_string).group().replace("<narr>", "").rstrip().replace("<desc> Description:", "").lstrip()
        desc = " ".join(desc.split()[3:]) # remove the first 3 words
        #print("desc contains:              ", desc)
        desc = desc.replace(" ", "%20") # HTML encoding for correct request with inurl
       #inurl = 'http://localhost:8983/solr/NLP_project/select?q='+title+'&fl=id%2Cscore&wt=json&indent=true&rows=20&qf=text_en^1.1%20text_de^1.1%20text_ru^0.3&defType=dismax'
        inurl = 'http://localhost:8983/solr/'+core_name+'/select?q=%27'+title+'%20'+desc+'%27&fl=DOCNO%2Cscore&wt=json&indent=true&rows=1000'
        data = urllib.request.urlopen(inurl)
        docs = json.load(data)['response']['docs']
        rank = 1
        for doc in docs:
           #f.write(num + ' ' + 'Q0' + ' ' + str(doc['DOCNO']) + ' ' + str(rank) + ' ' + str(doc['score']) + ' ' + IRModel + '\n')
            f.write(num + ' ' + 'Q0' + ' ' + doc['DOCNO'].strip() + ' ' + str(rank) + ' ' + str(doc['score']) + ' ' + IRModel + '\n')
           #query_id, iter, docno, rank, sim, run_id
            rank += 1

f.close()
queryFile.close()
print("SUCCESS!")


# In[ ]:




