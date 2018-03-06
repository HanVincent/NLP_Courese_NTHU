import re
from collections import Counter

def words(text): return re.findall(r'\w+', text.lower())

WORDS = Counter(words(open('big.txt').read()))

def P(word, N=sum(WORDS.values())): 
    "Probability of `word`."
    return WORDS[word] / N

def correction(word): 
    "Most probable spelling correction for word."
    states = [ ('', word, 0, P(word)) ]
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
        states = sorted(states, key=lambda x: x[3], reverse=True) [:100]# [:MAXBEAM]
    return states[:3]

def candidates(word): 
    "Generate possible spelling corrections for word."
    return (known([word]) or known(edits1(word)) or known(edits2(word)) or [word])

def known(words): 
    "The subset of `words` that appear in the dictionary of WORDS."
    return set(w for w in words if w in WORDS)

def next_states(state): # ('', word, 0, P[word])
    L, R, edit, prob = state
    R0, R1 = R[0], R[1:]
    if edit == 2: return []
    L = L + R0
    noedit = [(L, R1, edit, P(L + R1))]
    edit_once = [ (each, R1, edit+1, P(each + R1)) for each in edits1(L)]
    return set(noedit + edit_once)

def edits1(word):
    "All edits that are one edit away from `word`."
    letters    = 'abcdefghijklmnopqrstuvwxyz'
    splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
    deletes    = [L + R[1:]               for L, R in splits if R]
    replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
    inserts    = [L + c + R               for L, R in splits for c in letters if L]
    return set(deletes + replaces + inserts)
    
    # transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    # return set(deletes + transposes + replaces + inserts)

def edits2(word):
    "All edits that are two edits away from `word`."
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))

# print(correction('speling'))


from pprint import pprint

word =  'appearant'
pprint(next_states( ('', word, 0, P(word) )))
# pprint(correction(word))