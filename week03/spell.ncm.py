
# coding: utf-8

# In[1]:


from collections import Counter, defaultdict
import math, re
from pprint import pprint

count = dict()
count_c = defaultdict(lambda: 0)
for line in open('count_1edit.txt', 'r', encoding='utf8'):
    wc, num = line.strip().split('\t')
    w, c = wc.split('|')
    count[(w, c)] = int(num)
    count_c[c] += int(num)
Ncount = Counter(count.values())


# In[2]:


Nall = len(count.keys())
N0 = 26*26*26*26+2*26*26*26+26*26 - Nall
Nr = [ N0 if r == 0 else Ncount[r] for r in range(12) ]


# In[3]:


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


# In[4]:



def words(text): return re.findall(r'\w+', text.lower())
WORDS = Counter(words(open('big.txt').read()))
def Pw(word, N=sum(WORDS.values())): 
    "Probability of `word`."
    return WORDS[word] / N

def correction(word): 
    "Most probable spelling correction for word."
    states = [ ('', word, 0, Pw(word), 1) ]
    for i in range(len(word)):
        print(i, states[:3])
        STATES = [ s for state in states for s in next_states(state) ]
        states = sorted(STATES, key=lambda x: x[2])

        unique, new_states = set(), []
        for state in states:
            if state[0] + state[1] in unique: continue

            unique.add(state[0] + state[1])
            new_states.append(state)
        states = new_states
        states = sorted(states, key=lambda x: P(x[3], x[4]), reverse=True) [:500]# [:MAXBEAM]
    return states[:3]

def next_states(state):
    letters    = 'abcdefghijklmnopqrstuvwxyz'
    L, R, edit, prob, ped = state
    R0, R1 = R[0], R[1:]
    if edit == 2: return [( L + R0, R1, edit, prob, ped*0.8 )]
    noedit    = [( L + R0, R1, edit, prob, ped*0.8 )]
    delete    = [( L, R1, edit+1, Pw(L + R1), ped * Pedit(L[-1]+R0, L[-1]))]  if len(L) > 0 else []
    insert    = [( L + R0 + c, R1, edit+1, Pw(L + R0 + c + R1), ped * Pedit(R0, R0 + c) ) for c in letters]
    replace   = [( L + c, R1, edit+1, Pw(L + c + R1), ped * Pedit(R0, c) ) for c in letters]
    transpose = [( L[:-1] + R0, L[-1] + R1, edit+1, Pw(L[:-1] + R0 + L[-1] + R1), ped * Pedit(L[-1]+R0, R0+L[-1]) )] if len(L) > 1 else []
    return set(noedit + delete + replace + insert + transpose)

'''Combining channel probability with word probability to score states'''
def P(pw, pedit):
    return pw*pedit

# def spellAlign(word, correct):
#     L, R, edits = '', word, ''
#     states = [ [L, R, ''] ]
#     for i in range(len(word)+______ ):
#         states = [ state for states in map(next_states, states) for state in states ]
#         states = [ state for state in states if state[0] ___________________   )
#     states = [ state for state in states if state[0] ___________________ )
#     states.sort( ______________________________________________ )
#     return _____________________

pprint(correction('appearant'))
pprint(correction('runing'))
# pprint(correction('whou'))


# In[5]:


correction('thenks')


# In[6]:


correction('speling')

