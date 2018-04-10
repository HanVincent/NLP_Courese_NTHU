### reducer
import sys, re
from collections import defaultdict, Counter

HiFreWords = open('HiFreWords', 'r').read().split('\t')
Prons = open('prons.txt', 'r').read().split('\n')

def tokens(str1): return re.findall('[a-z]+', str1.lower()) 

def score(head, col, dist, s):
    tks = tokens(s)
    indices = [ i for i, t in enumerate(tks) if t == head ]
    if len(indices) == 1:
        loc = 0
    else:
        loc = [i for i in indices if i+int(dist) < len(tks) and i+int(dist) >= 0 and tks[i + int(dist)] == col][0]

    bad = sum([t not in HiFreWords and t in Prons for t in tks])
    return loc - bad

skipBigramExample = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: [])) )
for line in sys.stdin:
# for line in open('mapper.txt', 'r', encoding='utf8'):
    skip_gram, sent = line.split('\t')
    head, col, dist = skip_gram.split(' ')
    skipBigramExample[head][col][dist].append((sent, score(head, col, dist, sent)))
    
for head in skipBigramExample:
    for col in skipBigramExample[head]:
        for dist in skipBigramExample[head][col]:
            highest_sent = max(skipBigramExample[head][col][dist], key=lambda x: x[1])
            print("%s %s %s\t%s" % (head, col, dist, highest_sent[0]))
   