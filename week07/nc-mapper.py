### mapper

import re, sys
from collections import defaultdict, Counter

real_coll = defaultdict(lambda: defaultdict(Counter))
for line in open('bnc.coll.small.txt', 'r'):
    head, col, dist, count = line.split('\t')
    real_coll[head][col][dist] += int(count)
    
def tokens(str1): return re.findall('[a-z]+', str1.lower()) 

def ngrams(sent, n):
    return [ ' '.join(x) for x in zip(*[sent[i:] for i in range(n) if i <= len(sent) ] ) ]

def isCollocation(first, last, dist):
    return real_coll[first][last][str(dist)] >= 1
                            
for line in sys.stdin:
# for line in open('bnc.sents.txt', 'rt'):
    sent = tokens(line)
    for n in range(2, 6):
        for ngram in ngrams(sent, n):
            tks = ngram.split(' ')
            first, last = tks[0], tks[-1]

            if isCollocation(first, last, n-1) and len(sent) >= 10 and len(sent) <= 25:
                print("%s %s %s\t%s"%(first, last, n-1, line.strip()))
                print("%s %s %s\t%s"%(last, first, 1-n, line.strip()))