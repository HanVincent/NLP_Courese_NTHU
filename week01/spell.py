import re
from collections import Counter

def words(text): return re.findall(r'\w+', text.lower())

unigrams = words(open('big.txt').read())
bigrams = [' '.join(bi) for bi in zip(unigrams, unigrams[1:])]

WORDS = Counter(unigrams)
BI_WORDS = Counter(bigrams)

UNI_TOTAL = sum(WORDS.values())
BI_TOTAL = sum(BI_WORDS.values())

def P(word, N=UNI_TOTAL): 
    "Probability of `word`."
    return WORDS[word] / N or BI_WORDS[word] / BI_TOTAL

def correction(word): 
    "Most probable spelling correction for word."
    return max(candidates(word), key=P)

def candidates(word): 
    "Generate possible spelling corrections for word."
    return (known([word]) or edits1(word) or edits2(word) or [word])

def known(words): 
    "The subset of `words` that appear in the dictionary of WORDS."
    return set(w for w in words if w in WORDS or w in BI_WORDS)

def check_uni(candidates):
    return [word for word in candidates if all([token in WORDS for token in word.split()])]

def edits1(word):
    "All edits that are one edit away from `word`."
    letters    = 'abcdefghijklmnopqrstuvwxyz'
    splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
      
    fusions    = [L + ' ' + R             for L, R in splits if R] # get bigram candi dates
    deletes    = [L + R[1:]               for L, R in splits if R]

    prior1 = check_uni(set(fusions + deletes))
    if prior1: return prior1

    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
    inserts    = [L + c + R               for L, R in splits for c in letters]
    
    return check_uni(set(transposes + replaces + inserts))
    # return set(fusions + deletes + transposes + replaces + inserts)

def edits2(word):
    "All edits that are two edits away from `word`."
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))

print(correction('with out'))
print(correction('taketo'))
print(correction('mor efun'))