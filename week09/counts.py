
# coding: utf-8

# In[80]:


from collections import Counter, defaultdict
import numpy as np
import re


# In[81]:


tgts = open('./pat.txt', 'r', encoding='utf8').read().split('\n\n')

counts = defaultdict(Counter)
sents = defaultdict(lambda: defaultdict(lambda: []))


# In[82]:


for tgt in tgts:
    try:
        line, patterns = tgt.strip().split('\n', maxsplit=1)
    except:
        continue
    
    patterns = patterns.split('\n')
    
    for pattern in patterns:
        head, ptn, sent = pattern.split('\t')
        counts[head][ptn] += 1
        sents[head][ptn].append(sent)


# In[88]:



HiFreWords = open('HiFreWords', 'r').read().split('\t')
Prons = open('prons.txt', 'r').read().split('\n')

def getHighCounts(key, ngrams):
    new_counts = list(map(lambda pair: (pair[0], pair[1] * (len(pair[0].split(' '))**1.5)), ngrams.items()))

    values = list(map(lambda x: x[1], new_counts))
    total, avg, std = np.sum(values), np.mean(values), np.std(values)
    
    remains = filter(lambda pair: pair[1] > avg+std, new_counts)
    return remains


def tokens(str1): return re.findall('[a-z]+', str1.lower()) 

def score(head, sent):
    tks = tokens(sent)
    bad = sum([t not in HiFreWords and t in Prons for t in tks])
    return -bad

# VALUE, ALLOW, ABILITY, USEFUL, REMAIN, ESSENTIAL
target = ['VALUE-N', 'ALLOW-V', 'ABILITY-N', 'USEFUL-ADJ', 'REMAIN-V', 'ESSENTIAL-ADJ']
for head, ngrams in counts.items():
    if head not in target:
        continue
    
    remains = getHighCounts(head, ngrams)

    print(head.lower())
    for ptn, ctn in remains:
        highest_sent = max([ (sent, score(head, sent)) for sent in sents[head][ptn] ], key=lambda x: x[1])
        highest_sent = highest_sent[0]

        print("%s\t(%s)\t%s"%(ptn, str(counts[head][ptn]), highest_sent))
    print()

