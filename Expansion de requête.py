#!/usr/bin/env python
# coding: utf-8

# In[1]:


import nltk
from nltk.corpus import wordnet as wn
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import re
import os
from tqdm import tqdm
import xmltodict, json
import time
import urllib
import itertools
from nltk.corpus import wordnet
from nltk.corpus import stopwords
from nltk.stem.porter import *
from nltk.stem.snowball import SnowballStemmer


# In[2]:


def tokenizer(sentence):
    return word_tokenize(sentence)


# In[3]:


def pos_tagger(tokens):
    return nltk.pos_tag(tokens)


# In[4]:


def process_stopword(tokens):
    stopword = stopwords.words('english')
    result = []
    for token in tokens:
        if token[0].lower() not in stopword:
            result.append(tuple([token[0].lower(), token[1]]))
    return result


# In[5]:


pos_tag_map = {
    'NN': [ wn.NOUN ],
    'JJ': [ wn.ADJ, wn.ADJ_SAT ],
    'RB': [ wn.ADV ],
    'VB': [ wn.VERB ]
}

def pos_tag_converter(nltk_pos_tag):
    root_tag = nltk_pos_tag[0:2]
    try:
        pos_tag_map[root_tag]
        return pos_tag_map[root_tag]
    except KeyError:
        return ''


# In[6]:


def get_synsets(tokens):
    max_synsets = 1
    synsets = []
    for token in tokens:
        count = 0
        wn_pos_tag = pos_tag_converter(token[1])
        if wn_pos_tag == '':
            continue
        else:
            if count < max_synsets:
                synsets.append(wn.synsets(token[0], wn_pos_tag))
                count += 1
    return synsets


# In[7]:


def get_tokens_from_synsets(synsets):
    tokens = {}
    for synset in synsets:
        for s in synset:
            if s.name() in tokens:
                tokens[s.name().split('.')[0]] += 1
            else:
                tokens[s.name().split('.')[0]] = 1
    return tokens


# In[8]:


def get_hypernyms(synsets):
    hypernyms = []
    for synset in synsets:
        for s in synset:
            hypernyms.append(s.hypernyms())
    return hypernyms


# In[9]:


def get_tokens_from_hypernyms(synsets):
    tokens = {}
    for s in synsets:
        for ss in s:
            if ss.name().split('.')[0] in tokens:
                tokens[(ss.name().split('.')[0])] += 1
            else:
                tokens[(ss.name().split('.')[0])] = 1
    return tokens


# In[10]:


def underscore_replacer(tokens):
    new_tokens = {}
    for key in tokens.keys():
        mod_key = re.sub(r'_', ' ', key)
        new_tokens[mod_key] = tokens[key]
    return new_tokens


# In[11]:


def expand_query_with_synonyms(query):
    tokens = tokenizer(query)
    tokens = pos_tagger(tokens)
    tokens = process_stopword(tokens)
    synsets = get_synsets(tokens)
    synonyms = get_tokens_from_synsets(synsets)
    synonyms = underscore_replacer(synonyms)
    expanded_query = " ".join(list(synonyms.keys()))
    return expanded_query


# In[12]:


def get_wordnet_pos(treebank_tag):
    if treebank_tag[1].startswith('J'):
        return wn.ADJ
    elif treebank_tag[1].startswith('V'):
        return wn.VERB
    elif treebank_tag[1].startswith('N'):
        return wn.NOUN
    elif treebank_tag[1].startswith('R'):
        return wn.ADV
    else:
        return ''


# In[13]:


def expand_query_with_smart_synonyms(query):
    # stemmer = PorterStemmer()
    stemmer = SnowballStemmer("english")

    #queryList = "this is a first query \n and this is a second one"

    #for query in queryList:

    querySplitted = query.split(" ")

    # tokenizing the query
    tokens = word_tokenize(query)

    # removing stop words in the query
    filtered_words = [word for word in tokens if word not in stopwords.words('english')]

    # pos tagging of tokens
    pos = nltk.pos_tag(filtered_words)

    #print('pos: ', pos)

    synonyms = []  # synonyms of all the tokens

    index = 0
    # iterating through the tokens
    for item in filtered_words:
        synsets = wn.synsets(item)

        if not synsets:
            # stemming the tokens in the query
            synsets = wn.synsets(stemmer.stem(item))

        # synonyms of the current token
        currentSynonyms = []
        currentPOS = get_wordnet_pos(pos[index])

        count=0
        
        max_synonyms = 1
        
        for syn in synsets:
            if str(syn.pos()) == str(currentPOS):
                for l in syn.lemmas() :
                    if(count < max_synonyms):
                        if l.name() not in currentSynonyms:
                            currentSynonyms.append(l.name())
                            count+=1
            synonyms.append(currentSynonyms)

        # iterating through the synsets
        '''for i in synsets:
            # first we check if token and synset have the same part of speech
            #print('i ', i)
            #print('str(i.pos())', str(i.pos()))
            #print('str(currentPOS)', str(currentPOS))
            if str(i.pos()) == str(currentPOS):
                for j in i.lemmas():
                    if j.name() not in currentSynonyms:  # if we have not
                        currentSynonyms.append(j.name().replace("_", " "))
            synonyms.append(currentSynonyms)
            #print("current state of synonyms: ", synonyms)'''
        index += 1

    #f.write(querySplitted[0] + ", " + querySplitted[1] + ", ")

    # removing duplicate lists in the synonyms list
    synonyms = [item for sublist in synonyms for item in sublist]
    tmp = []
    for elem in synonyms:
        if elem and elem not in tmp:
            tmp.append(elem)
    synonyms = tmp
    
    synonyms = " ".join(list(synonyms))
    synonyms = synonyms.split()
    synonyms = list( dict.fromkeys(synonyms) )
    synonyms = [word for word in synonyms if word not in stopwords.words('english')]
    expanded_query = " ".join(list(synonyms))

    return expanded_query


# In[14]:


expand_query_with_smart_synonyms("this is a date")


# In[15]:


def expand_query_with_hypernyms(query):
    tokens = tokenizer(query)
    tokens = pos_tagger(tokens)
    tokens = process_stopword(tokens)
    synsets = get_synsets(tokens)
    hypernyms = get_hypernyms(synsets)
    hypernyms = get_tokens_from_hypernyms(hypernyms)
    hypernyms = underscore_replacer(hypernyms)
    expanded_query = " ".join(list(hypernyms.keys()))
    return expanded_query


# In[16]:


def expand_query_with_synonyms_and_hypernyms(query):
    tokens = tokenizer(query)
    tokens = pos_tagger(tokens)
    tokens = process_stopword(tokens)
    synsets = get_synsets(tokens)
    synonyms = get_tokens_from_synsets(synsets)
    synonyms = underscore_replacer(synonyms)
    #lemmas = expand_query_with_lemmas
    hypernyms = get_hypernyms(synsets)
    hypernyms = get_tokens_from_hypernyms(hypernyms)
    hypernyms = underscore_replacer(hypernyms)
    tokens = {**synonyms, **hypernyms}
    expanded_query = " ".join(list(tokens.keys()))
    return expanded_query


# In[17]:


def expand_query_with_lemmas(query):
    max_lemmas = 1
    tokenized_query = word_tokenize(query)
    stopwordz = stopwords.words('english')
    tokenized_query_without_stopwords = []
    for token in tokenized_query:
        if token.lower() not in stopwordz:
            tokenized_query_without_stopwords.append(token.lower())
    lemmas = []
    for token in tokenized_query_without_stopwords:
        count = 0
        for syn in wn.synsets(token):
            for l in syn.lemmas():
                if count < max_lemmas:
                    lemma = l.name()
                    lemmas.append(re.sub(r'_', ' ', lemma))
                    count += 1
    lemmas = " ".join(lemmas)
    lemmas = lemmas.split()
    lemmas = list( dict.fromkeys(lemmas) )
    return(" ".join(lemmas))


# In[18]:


def expand_query_with_synonyms_and_lemmas(query):
    expanded_query_with_synonyms = expand_query_with_synonyms(query)
    expanded_query_with_lemmas = expand_query_with_lemmas(query)
    expanded_query_with_synonyms_and_lemmas = expanded_query_with_synonyms + expanded_query_with_lemmas
    return expanded_query_with_synonyms_and_lemmas


# In[19]:


def expand_query_with_hypernyms_and_lemmas(query):
    expanded_query_with_hypernyms = expand_query_with_hypernyms(query)
    expanded_query_with_lemmas = expand_query_with_lemmas(query)
    expanded_query_with_hypernyms_and_lemmas = expanded_query_with_hypernyms + expanded_query_with_lemmas
    return expanded_query_with_hypernyms_and_lemmas


# In[20]:


def expand_query_with_synonyms_hypernyms_and_lemmas(query):
    expanded_query_with_hypernyms = expand_query_with_hypernyms(query)
    expanded_query_with_synonyms = expand_query_with_synonyms(query)
    expanded_query_with_lemmas = expand_query_with_lemmas(query)
    expanded_query_with_synonyms_hypernyms_and_lemmas = expanded_query_with_synonyms + expanded_query_with_hypernyms + expanded_query_with_lemmas
    return expanded_query_with_synonyms_hypernyms_and_lemmas


# In[21]:


def identical_query(query):
    return query


# In[22]:


query = "hello my name is ahmed"
print("Query:")
print(query)
print()
print("Expanded query with synonyms becomes: ")
print(expand_query_with_synonyms(query))
print()
print("Expanded query with smart synonyms becomes: ")
print(expand_query_with_smart_synonyms(query))
print()
print("Expanded query with hypernyms becomes: ")
print(expand_query_with_hypernyms(query))
print()
print("Expanded query with lemmas becomes: ")
print(expand_query_with_lemmas(query))
print()
print("Expanded query with synonyms and hypernyms becomes: ")
print(expand_query_with_synonyms_and_hypernyms(query))
print()
print("Expanded query with synonyms and lemmas becomes: ")
print(expand_query_with_synonyms_and_lemmas(query))
print()
print("Expanded query with hypernyms and lemmas becomes: ")
print(expand_query_with_hypernyms_and_lemmas(query))
print()
print("Expanded query with synonyms, hypernyms and lemmas becomes: ")
print(expand_query_with_synonyms_hypernyms_and_lemmas(query))


# In[25]:


query = "This is a sample query for the IR system."
print("query: ", query)
tokens = tokenizer(query)
print("tokens: ", tokens)
tokens = pos_tagger(tokens)
print("tokens: ", tokens)
tokens = process_stopword(tokens)
print("tokens: ", tokens)
synsets = get_synsets(tokens)
print("synsets: ", synsets)
synonyms = get_tokens_from_synsets(synsets)
print("synonyms: ", synonyms)
synonyms = underscore_replacer(synonyms)
print("synonyms: ", synonyms)
expanded_query = " ".join(list(synonyms.keys()))
print("expanded query: ", expanded_query + " " + query)


# In[ ]:





# In[ ]:





# # Using expanded queries

# In[36]:


## Reqêtes longues avec BM25 ##
core_name = "NLP_advanced_BM25"
i = 0
expansion_functions_list = [expand_query_with_synonyms, expand_query_with_hypernyms, expand_query_with_lemmas,                            expand_query_with_synonyms_and_hypernyms, expand_query_with_synonyms_and_lemmas,                            expand_query_with_hypernyms_and_lemmas, expand_query_with_smart_synonyms,                            expand_query_with_synonyms_hypernyms_and_lemmas, identical_query]
for fn in expansion_functions_list: 
    i = i + 1
    print("Processing expansion {} of {} ({})..".format(i, len(expansion_functions_list), fn.__name__))
    outputFile = 'expanded_using_' + fn.__name__ + '.txt'
    print("outputFile", outputFile)
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
            title = title.replace("\n", "") 
        
        if q.strip().startswith("<desc>"):
            desc = re.match('.*?Document.*?<narr>', queries_string).group().replace("<narr>", "").rstrip().replace("<desc> Description:", "").lstrip()
            desc = " ".join(desc.split()[3:]) # remove the first 3 words
            
            # expanding query
            #expanded_query = fn(title+'%20'+desc)
            query = title.replace(" ", "%20") + "%20" + desc.replace(" ", "%20")
            expanded_query = fn(title +" " + desc)
            #expanded_query = expanded_query + "%20" + title + '%20' + desc
            expanded_query = expanded_query.replace(" ", "%20")
            inurl = 'http://localhost:8983/solr/'+core_name+'/select?q=%27'+query+"%20"+expanded_query+'%27&fl=DOCNO%2Cscore&wt=json&indent=true&rows=1000'
            data = urllib.request.urlopen(inurl)
            docs = json.load(data)['response']['docs']
            rank = 1
            for doc in docs:
                f.write(num + ' ' + 'Q0' + ' ' + doc['DOCNO'].strip() + ' ' + str(rank) + ' ' + str(doc['score']) + ' ' + IRModel + '\n')
                rank += 1
    f.close()
    queryFile.close()
    print("SUCCESS!")


# In[25]:


from nltk.corpus import brown
freqs = nltk.FreqDist(w.lower() for w in brown.words())
print(freqs["hello"])


# In[26]:


import itertools
import nltk
from nltk.corpus import wordnet
from nltk.corpus import stopwords
from nltk.stem.porter import *
from nltk.stem.snowball import SnowballStemmer


def run(queryList):

    # stemmer = PorterStemmer()
    stemmer = SnowballStemmer("english")

    f = open("data/expanded.txt", "w+")
    for query in queryList:
        querySplitted = query.split(",")

        # tokenizing the query
        tokens = nltk.word_tokenize(querySplitted[1])

        # removing stop words in the query
        filtered_words = [word for word in tokens if word not in stopwords.words('english')]

        # pos tagging of tokens
        pos = nltk.pos_tag(filtered_words)

        synonyms = []  # synonyms of all the tokens

        index = 0
        # iterating through the tokens
        for item in filtered_words:
            synsets = wn.synsets(item)

            if not synsets:
                # stemming the tokens in the query
                synsets = wn.synsets(stemmer.stem(item))

            # synonyms of the current token
            currentSynonyms = []
            currentPOS = get_wordnet_pos(pos[index])

            # iterating through the synsets
            for i in synsets:
                # first we check if token and synset have the same part of speech
                if str(i.pos()) == str(currentPOS):
                    for j in i.lemmas():
                        if j.name() not in currentSynonyms:  # if we have not
                            currentSynonyms.append(j.name().replace("_", " "))
                synonyms.append(currentSynonyms)
            index += 1

        f.write(querySplitted[0] + ", " + querySplitted[1] + ", ")

        # removing duplicate lists in the synonyms list
        tmp = []
        for elem in synonyms:
            if elem and elem not in tmp:
                tmp.append(elem)
        synonyms = tmp

        # now that we have all the synonyms
        for x in itertools.product(*synonyms):
            current = ""
            for item in x:
                current += item
                current += " "
            current += ", "
            f.write(current)
        f.write("\n")


def get_wordnet_pos(treebank_tag):

    if treebank_tag[1].startswith('J'):
        return wn.ADJ
    elif treebank_tag[1].startswith('V'):
        return wn.VERB
    elif treebank_tag[1].startswith('N'):
        return wn.NOUN
    elif treebank_tag[1].startswith('R'):
        return wn.ADV
    else:
        return ''


# In[ ]:





# In[27]:


from nltk.stem.snowball import SnowballStemmer
stemmer = SnowballStemmer("english")


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




