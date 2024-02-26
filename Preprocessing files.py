#!/usr/bin/env python
# coding: utf-8

# In[3]:


import os
from tqdm import tqdm
import xmltodict, json
import time


# In[31]:


def line_prepender(filename, line_in_beginning, line_in_ending):
    with open(filename, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(line_in_beginning.rstrip('\r\n') + '\n' + content)
        f.write(line_in_ending)


# ## Adding "< add>" before the beginning of each document and "< /add>" at the end

# In[32]:


directory = "C:\solr-8.10.0\solr-8.10.0\Extracted_documents"

for filename in tqdm(os.listdir(directory)):
    if filename != ".ipynb_checkpoints":
        line_prepender(directory+"/"+filename, '<add>', '\n</add>')        


# ## Replacing < DOCNO> with < field name="id> and so on..

# In[33]:


#directory = "C:\\solr-8.10.0\\solr-8.10.0\\Extracted_documents_reduced_list"
directory = "C:\\solr-8.10.0\\solr-8.10.0\\Extracted_documents"

to_replace_list = ["<DOCNO>", "<FILEID>", "<FIRST>", "<SECOND>", "<HEAD>", "<DATELINE>", "<TEXT>","<BYLINE>", "<NOTE>", "<UNK>",                   "</DOCNO>", "</FILEID>", "</FIRST>", "</SECOND>", "</HEAD>", "</DATELINE>", "</TEXT>", "</BYLINE>", "</NOTE>", "</UNK>"]
replacing_list = ['<field name="DOCNO">', '<field name="FILEID">', '<field name="FIRST">', '<field name="SECOND">',                  '<field name="HEAD">', '<field name="DATELINE">', '<field name="TEXT">', '<field name="BYLINE">', '<field name="NOTE">', '<field name="UNK">',                  '</field>', '</field>', '</field>', '</field>', '</field>', '</field>', '</field>', '</field>', '</field>', '</field>']

for filename in tqdm(os.listdir(directory)):
    if filename != ".ipynb_checkpoints":
        with open(directory + "/" + filename, 'r') as file :
            # Read in the file
            filedata = file.read()
            filedata = filedata.replace("\n", "\n    ")
            filedata = filedata.replace("\n    <DOC>", "\n  <DOC>")    
            filedata = filedata.replace("\n    </add>", "\n</add>")    
            filedata = filedata.replace("DOC>", "doc>") 
            
            filedata = filedata.replace(" & ", " &amp; ") 
            filedata = filedata.replace(" &\n", " &amp;\n") 
            
            filedata = filedata.replace("&lsqb;", "[") 
            filedata = filedata.replace("&rsqb;", "]") 
            filedata = filedata.replace("&plus;", "+") 
            filedata = filedata.replace("&equals;", "=") 

            #filedata = filedata.replace("<DOC>", "<doc>")
            #filedata = filedata.replace("</DOC>", "</doc>")  
            
            
        for  i in range(len(to_replace_list)):
            # Replace the target string
            filedata = filedata.replace(to_replace_list[i], replacing_list[i])

        # Write the file out again
        with open(directory + "/" + filename, 'w') as file:
            file.write(filedata)


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# # Evaluation du système RI

# ### Requêtes courtes (champ "title" seulement)

# In[66]:


# -*- coding: utf-8 -*-
"""
A program to do the following:
- Run multiple queries on a Solr instance (fetched from a text file)
- Format for input query is xxx <Query>, 
	where xxx is the query number and <Query> is the query text
- Save the returned output in a file in Trec format for the Trec Evaluation 
Thanks to the author Ruhan Sa, who was the TA of IR Project 3 in Fall 2015 for providing the
initial code
"""
import json
import urllib


outputFile = 'dfr-output.txt'
f = open(outputFile, 'w')
queryFile = open('queries.txt')
queries = queryFile.readlines();
qId = ''
qText = ''
#IRModel='DFR'
IRModel='STANDARD'


# In[67]:


for q in queries:
    q = q.replace("  ", " ")
    # deal with the document number qID
    if q.strip().startswith("<num>"):
        num = str(int(q.split(" ")[2].strip()))
        
    if q.strip().startswith("<title>"):
        title = q.split(" ", 2)[2]
        title = title.replace(" ", "%20")
        title = title.replace("\n", "") 
       #inurl = 'http://localhost:8983/solr/NLP_project/select?q='+title+'&fl=id%2Cscore&wt=json&indent=true&rows=20&qf=text_en^1.1%20text_de^1.1%20text_ru^0.3&defType=dismax'
        inurl = 'http://localhost:8983/solr/testing_collection/select?q=%27'+title+'%27&fl=DOCNO%2Cscore&wt=json&indent=true&rows=20'
        data = urllib.request.urlopen(inurl)
        docs = json.load(data)['response']['docs']
        rank = 1
        for doc in docs:
           #f.write(num + ' ' + 'Q0' + ' ' + str(doc['DOCNO']) + ' ' + str(rank) + ' ' + str(doc['score']) + ' ' + IRModel + '\n')
            f.write(num + ' ' + 'Q0' + ' ' + doc['DOCNO'][0].strip() + ' ' + str(rank) + ' ' + str(doc['score']) + ' ' + IRModel + '\n')
           #query_id, iter, docno, rank, sim, run_id
            rank += 1

f.close()
queryFile.close()


# In[59]:


inurl


# ### Requêtes longues (champ "title" seulement)

# In[107]:


# -*- coding: utf-8 -*-
"""
A program to do the following:
- Run multiple queries on a Solr instance (fetched from a text file)
- Format for input query is xxx <Query>, 
	where xxx is the query number and <Query> is the query text
- Save the returned output in a file in Trec format for the Trec Evaluation 
Thanks to the author Ruhan Sa, who was the TA of IR Project 3 in Fall 2015 for providing the
initial code
"""
import json
import urllib


outputFile = 'dfr-output.txt'
f = open(outputFile, 'w')
queryFile = open('queries.txt')
queries = queryFile.readlines();
qId = ''
qText = ''
#IRModel='DFR'
IRModel='STANDARD'


# In[108]:


import re
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
        #inurl = 'http://localhost:8983/solr/NLP_project/select?q=%27'+title+desc+'%27&fl=DOCNO%2Cscore&wt=json&indent=true&rows=20'
        inurl = 'http://localhost:8983/solr/'+core_name+'/select?q=%27'+title+desc+'%27&fl=DOCNO%2Cscore&wt=json&indent=true&rows=100'
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


# In[25]:


'hello'[2]


# In[105]:


doc


# In[183]:


queries_string.removeprefix(q.replace("\n", " "))


# In[157]:


q


# In[33]:


from itertools import islice
queries_iter = iter(queries)
for q in queries_iter:
    print(q)        
    if q.strip().startswith("<desc>"):
        print("hello this is q before skipping: ", q)
        #next(queries_iter)
        #next(queries_iter)
        print("hello this is q after skipping: ", next(islice(queries_iter, 1, 2)))


# In[38]:


import re

string = "asdasd dwref ADSADSADA Hello i'm Gabi :D goodbye asd asl sodjasdji asdoija"


match = re.findall(r'hello .+ goodbye', string, flags=re.IGNORECASE)
if match:
    print(match[0])


# In[51]:


string = '<head> Tipster Topic Description\n \n <num> Number: 001\n \n <dom> Domain: International Economics\n \n <title> Topic: Antitrust Cases Pending\n \n \n <desc> Description:\n \n Document discusses a pending antitrust case.\n \n \n <narr> Narrative:\n \n To be relevant, a document'


# In[94]:


import re
#match = re.findall(r'<desc> Description: .+ <narr>', " ".join(queries), flags=re.IGNORECASE)
string = " ".join(queries)
string = string.replace("\n", " ")
match = re.findall(r'Document discusses .+ <narr>', string, flags=re.MULTILINE)
if match:
    print(match[0])


# In[141]:


q


# In[138]:


re.match('.*?<desc> Description:.*?<narr>', string).group()


# In[118]:


string

