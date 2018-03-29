
# coding: utf-8

# In[15]:

#from nltk.corpus import wordnet as wn
import re, random, nltk, json
from pprint import pprint
from collections import defaultdict, Counter
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.probability import DictionaryProbDist as D


def words(text): return re.findall(r'\w+', text.lower())

def wnTag(pos): return {'noun': 'n', 'verb': 'v', 'adjective': 'a', 'adverb': 'r'}[pos]

def split_col(data):
    training = [ line.strip().split('\t') for line in data if line.strip() != '' ]
    return training

lmtzr = WordNetLemmatizer()

def isHead(head, word, tag):
    try:
        return lmtzr.lemmatize(word, tag) == head
    except:
        return False
        
TF = defaultdict(lambda: Counter())
DF = defaultdict(lambda: [])

def set_TF_DF(training):   
    for wnid, wncat, senseDef, target in training:
        head, pos = wnid.split('-')[:2]
        for word in words(senseDef):
            if word != head and not isHead(head, word, pos):
                TF[word][wncat] += 1
                DF[word] += [] if wncat in DF[word] else [wncat]   


# In[16]:

data = open('wn.in.evp.cat.txt', 'r').readlines()[:]
random.shuffle(data)
data = split_col(data)
split_point = len(data)*9//10
train_set, test_set = data[:split_point], data[split_point:]
set_TF_DF(train_set)

nTF = sorted(TF, key=lambda k: sum(TF[k].values()),reverse=True)[:200]
nDF = sorted(DF, key=lambda k: len(DF[k]),reverse=True)[:200]
stopwords = set(nTF).intersection(set(nDF))


# In[17]:

print(train_set[0])


# In[18]:

def gender_features(wnid, wncat, senseDef, target):
    head, pos = wnid.split('-')[:2]
    features = {'pos': pos}
    for word in words(senseDef):
        if word in stopwords: continue

        if word != head and not isHead(head, word, pos): # 有需要過濾自己嗎？
            for cat, count in TF[word].most_common(10):
                features.update({cat: count * 1000/len(DF[word])}) # tf*int(1000/df)
    return (features, wncat)
    
    
def LG_gender(train_set):
    print('== SkLearn MaxEnt ==')
    
    from nltk.classify import SklearnClassifier 
    from sklearn.linear_model import LogisticRegression
    
    sklearn_classifier = SklearnClassifier(LogisticRegression(C=10e5)).train(train_set)
    return sklearn_classifier


# In[19]:

pprint(gender_features(*train_set[0])) # 看 feature


# In[ ]:




# In[21]:

# train
train_featuresets = [ gender_features(*x) for x in train_set ]
test_featuresets = [ gender_features(*x) for x in test_set ]
sklearn_classifier = LG_gender(train_featuresets)


# In[23]:

# predict
print(nltk.classify.accuracy(sklearn_classifier, test_featuresets)) # 未過濾
    
correct = 0
for i, (feature, label) in enumerate(test_featuresets):
    prob_dict = sklearn_classifier.prob_classify(test_featuresets[i][0])._prob_dict

    targets = json.loads(test_set[i][3].replace("'", '"')).values()
    probs = [(target, prob_dict[target]) for target in targets if target in prob_dict]
    if not probs:
        if max(prob_dict.items(), key=lambda x: x[1])[0] == label:
            correct+=1
    else: 
        if max(probs, key=lambda x: x[1])[0] == label:
            correct+=1
print(correct/len(test_featuresets))
    
    
    
#     data = open('evp.in.wn.cat.txt', 'r').readlines()
#     testing = split_col(data)
#     test_featuresets = [ gender_features(*x) for x in testing ]
    
#     fs = open('result.txt', 'w', encoding='utf8')

#     for i, (feature, label) in enumerate(test_featuresets):
#         prob_dict = sklearn_classifier.prob_classify(test_featuresets[i][0])._prob_dict

#         targets = json.loads(testing[i][3].replace("'", '"')).values()
#         probs = [(target, prob_dict[target]) for target in targets if target in prob_dict]
#         if not probs:
#             print()
#         else: 

#     fs.close()


# In[9]:




# In[14]:

# top_5_model = sklearn_classifier
# top_10_model = sklearn_classifier


# In[ ]:



