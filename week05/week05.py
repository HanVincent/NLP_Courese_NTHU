
# coding: utf-8

# In[1]:


#from nltk.corpus import wordnet as wn
import re
from pprint import pprint
from collections import defaultdict, Counter
from nltk.stem.wordnet import WordNetLemmatizer
lmtzr = WordNetLemmatizer()
import nltk, random
from nltk.probability import DictionaryProbDist as D


def words(text): return re.findall(r'\w+', text.lower())

def wnTag(pos): return {'noun': 'n', 'verb': 'v', 'adjective': 'a', 'adverb': 'r'}[pos]

TF = defaultdict(lambda: Counter())
DF = defaultdict(lambda: [])


def split_col(data):
    training = [  line.strip().split('\t') for line in data if line.strip() != '' ]
    return training


def isHead(head, word, tag):
    try:
        return lmtzr.lemmatize(word, tag) == head
    except:
        return False
        
    
def set_TF_DF(training):   
    for wnid, wncat, senseDef, target in training:
        head, pos = wnid.split('-')[:2]
        for word in words(senseDef):
            if word != head and not isHead(head, word, pos):
                TF[word][wncat] += 1
                DF[word] += [] if wncat in DF[word] else [wncat]   
    
    
def gender_features(wnid, wncat, senseDef, target):
    head, pos = wnid.split('-')[:2]
    features = {'pos': pos}
    for word in words(senseDef):
        if word != head and not isHead(head, word, pos): # 有需要過濾自己嗎？
            for cat, count in TF[word].most_common(3):
                features.update({cat: count / len(DF[word])}) # tf*int(1000/df)
    return (features, wncat)
    
    
def LG_gender(train_set, test_set, origin_test=None):
    print('== SkLearn MaxEnt ==')
    
    from nltk.classify import SklearnClassifier 
    from sklearn.linear_model import LogisticRegression
    
    sklearn_classifier = SklearnClassifier(LogisticRegression(C=10e5)).train(train_set)
    return sklearn_classifier


# In[71]:


import json
if __name__ == '__main__':
    data = open('wn.in.evp.cat.txt', 'r').readlines()
#     random.shuffle(data)
    split_point = len(data)*9//10
    train_set, test_set = data[:split_point], data[split_point:]

    training = split_col(train_set)
    testing = split_col(test_set)
    set_TF_DF(training)
    
#     pprint(gender_features(*training[0])) # 看 feature
    
    train_featuresets = [ gender_features(*x) for x in training ]
    test_featuresets = [ gender_features(*x) for x in testing ]
    sklearn_classifier = LG_gender(train_featuresets, test_featuresets)
 

    print(nltk.classify.accuracy(sklearn_classifier, test_featuresets)) # 未過濾
    

    correct = 0
    for i, (feature, label) in enumerate(test_featuresets):
        prob_dict = sklearn_classifier.prob_classify(test_featuresets[i][0])._prob_dict

        targets = json.loads(testing[i][3].replace("'", '"')).values()
        probs = [(target, prob_dict[target]) for target in targets if target in prob_dict]
        if not probs:
            if max(prob_dict.items(), key=lambda x: x[1])[0] == label:
                correct+=1
        else: 
            if max(probs, key=lambda x: x[1])[0] == label:
                correct+=1
    print(correct/len(test_featuresets))
    

