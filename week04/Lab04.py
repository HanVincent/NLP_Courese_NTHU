
# coding: utf-8

# In[5]:


import math, re
from pprint import pprint
from collections import Counter, defaultdict

count = dict()
count_c = defaultdict(lambda: 0)
for line in open('count_1edit.txt', 'r', encoding='utf8'):
    wc, num = line.strip().split('\t')
    w, c = wc.split('|')
    count[(w, c)] = int(num)
    count_c[c] += int(num)
Ncount = Counter(count.values())

Nall = len(count.keys())
N0 = 26*26*26*26+2*26*26*26+26*26 - Nall
Nr = [ N0 if r == 0 else Ncount[r] for r in range(12) ]

def smooth(count, r=10):
    if count <= r:
        return (count+1)*Nr[count+1] / Nr[count]
    else:
        return count

def Pedit(w, c):
    if (w, c) not in count and count_c[c] > 0:
        return smooth(0) / count_c[c]
    if count_c[c] > 0:
        return smooth(count[(w, c)]) / count_c[c]
    else:
        return 0

def words(text): return re.findall(r'\w+', text.lower())

WORDS = Counter(words(open('big.txt').read()))
# WORDS = Counter(open('big.txt').read().split())

def Pw(word, N=sum(WORDS.values())): 
    "Probability of `word`."
    return WORDS[word] / N

def correction(word): 
    "Most probable spelling correction for word."
    states = [ ('', word, 0, Pw(word), 1) ]
    for i in range(len(word)):
        # print(i, states[:3])
        STATES = [ s for state in states for s in next_states(state) ]
        states = sorted(STATES, key=lambda x: x[2])

        unique, new_states = set(), []
        for state in states:
            if state[0] + state[1] in unique: continue

            unique.add(state[0] + state[1])
            new_states.append(state)
        states = new_states
        states = sorted(states, key=lambda x: P(x[3], x[4]), reverse=True) [:500]# [:MAXBEAM]
    return states[:10]

def next_states(state):
    letters    = 'abcdefghijklmnopqrstuvwxyz'
    L, R, edit, prob, ped = state
    R0, R1 = R[0], R[1:]
    if edit == 2: return [( L + R0, R1, edit, prob, ped*0.8 )]
    noedit    = [( L + R0, R1, edit, prob, ped*0.8 )]
    delete    = [( L, R1, edit+1, Pw(L + R1), ped * Pedit(L[-1]+R0, L[-1]))]  if len(L) > 0 else []
    insert    = [( L + R0 + c, R1, edit+1, Pw(L + R0 + c + R1), ped * Pedit(R0, R0 + c) ) for c in letters]
    replace   = [( L + c, R1, edit+1, Pw(L + c + R1), ped * Pedit(R0, c) ) for c in letters]
    transpose = [( L[:-1] + R0 + L[-1], R1, edit+1, Pw(L[:-1] + R0 + L[-1] + R1), ped * Pedit(L[-1]+R0, R0+L[-1]) )] if len(L) > 1 else []
    return set(noedit + delete + replace + insert + transpose)

'''Combining channel probability with word probability to score states'''
def P(pw, pedit):
    return pw*pedit


# In[6]:


import requests

API_URL = "http://api.netspeak.org/netspeak3/search?query=%s"

class NetSpeak:
    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 5.5; Windows NT)'}
        self.page = None
        self.dictionary = {}

    def __getPageContent(self, url):
        return requests.get(url, headers=self.headers).text
        # return self.opener.open(url).read()

    def __rolling(self, url, maxfreq=None):
        if maxfreq:
            webdata = self.__getPageContent(url + "&maxfreq=%s" % maxfreq)
        else:
            webdata = self.__getPageContent(url)
        if webdata:
            # webdata = webdata.decode('utf-8')
            results = [data.split('\t') for data in webdata.splitlines()]
            results = [(data[2], float(data[1])) for data in results]
            lastFreq = int(results[-1][1])
            if lastFreq != maxfreq:
                return results + self.__rolling(url, lastFreq)
            else:
                return []
        else:
            return []

    def search(self, query):
        if query in self.dictionary: return self.dictionary[query]
        
        queries = query.lower().split()
        new_query = []
        for token in queries:
            if token.count('|') > 0:
                new_query.append('[+{0}+]'.format('+'.join(token.split('|'))))
            elif token == '*':
                new_query.append('?')
            else:
                new_query.append(token)
        new_query = '+'.join(new_query)
        url = API_URL % (new_query.replace(' ', '+'))
        self.dictionary[query] = self.__rolling(url)
        return self.dictionary[query]
    
SE = NetSpeak() # singleton


# In[7]:


confusable = dict([line.strip().split('\t') for line in open('lab4.confusables.txt', 'r', encoding='utf8')])

def get_trigrams(tokens):
    return [tokens[i:i+3] for i in range(len(tokens) - 2)]

def get_lowest_tri(tokens):
    trigrams, pairs = get_trigrams(tokens), [] # (index, count, trigram)
    for i, tri in enumerate(trigrams):
        res = SE.search(' '.join(tri))
        if res:
            pairs.append((i, res[0][1], tri))
        else:
            pairs.append((i, 0, tri))

    minimum = min(pairs, key=lambda x: x[1])[1]
    pairs = [p for p in pairs if p[1] == minimum]
    
    lowest_pair = pairs[0]
    lowest_start = lowest_pair[0]
    
    return lowest_pair, lowest_start

def get_max_sent(tokens, lowest_start):
    # (sent, error_word, correct_token, can_tokens, count)
    best = (None, None, None, None, -math.inf)
    
    for i in range(lowest_start, lowest_start + 3):
        can_tokens = [can[0] for can in correction(tokens[i])] + ([confusable[tokens[i]]] if tokens[i] in confusable else [])
        for c in can_tokens: # get correction candidates (a word)
            count = 1.0
            sent = tokens[:i] + [c] + tokens[i+1:]
            trigrams = get_trigrams(sent)
        
            for tri in trigrams:
                res = SE.search(' '.join(tri))
                count *= res[0][1] if res else 0

            best = (sent, tokens[i], c, can_tokens, count) if count > best[-1] else best
    return best


# In[9]:


# lines = ['I was on an exclation 	I was on an escalator', 'to tidy up his gardon 	to tidy up his garden','talk to the manger 	talk to the manager', 'through the fance 	through the fence']

cor, hits = 0, 0
lines = open('lab4.test.1.txt', 'r', encoding='utf8').readlines()[:20]
result = open('result.txt', 'w', encoding='utf8')

for i, line in enumerate(lines):
# for line in lines:
    print("================", i+1, "===================", file=result)
    wrong, right = line.split('\t')

    tokens = wrong.strip().split(' ') # words(open('big.txt').read())) # or using regex
    lowest_pair, lowest_pos = get_lowest_tri(tokens)
    
    sent, error_word, right_word, candidates, _ = get_max_sent(tokens, lowest_pos)
    sent, wrong, right = ' '.join(sent).strip(), wrong.strip(), right.strip()
    
    if sent == right: hits += 1
    cor += 1
    
    print("Error:", error_word, file=result)
    print("Candidates:", candidates, file=result)
    print("Correction:", right_word, file=result)
    print(wrong, "->", sent, "(correct:", right, ")", file=result)
    print("hits =", hits, file=result)
    print('\n', file=result)

print("Precision:", hits/cor, file=result)
print("FalseAlarm:", (cor-hits)/cor, file=result)

result.close()


# In[ ]:


################### BONUS ######################
cor, hits = 0, 0
lines = open('lab4.test.1.txt', 'r', encoding='utf8').readlines()[:20]
result = open('result.txt', 'w', encoding='utf8')

for i, line in enumerate(lines):
# for line in lines:
    print("================", i+1, "===================", file=result)
    wrong, right = line.split('\t')

    tokens = wrong.strip().split(' ') # words(open('big.txt').read())) # or using regex
    lowest_pair, lowest_pos = get_lowest_tri(tokens)
    
    sent, error_word, right_word, candidates, _ = get_max_sent(tokens, lowest_pos)
    sent, wrong, right = ' '.join(sent).strip(), wrong.strip(), right.strip()
    
    if sent == right: hits += 1
    cor += 1
    
    print("Error:", error_word, file=result)
    print("Candidates:", candidates, file=result)
    print("Correction:", right_word, file=result)
    print(wrong, "->", sent, "(correct:", right, ")", file=result)
    print("hits =", hits, file=result)
    print('\n', file=result)

print("Precision:", hits/cor, file=result)
print("FalseAlarm:", (cor-hits)/cor, file=result)

result.close()

