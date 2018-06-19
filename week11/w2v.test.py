from gensim.models import KeyedVectors

wndict = dict( [ tuple(x.strip().split('\t')[0::3]) for x in open('w2v.voc.in.dict.txt','r').readlines() ] )
model = KeyedVectors.load_word2vec_format('GoogleNews-vectors-negative300.bin.gz', binary=True)
 
print ("""Usage\n\tmodel.most_similar(positive=['woman', 'king'], negative=['man'], topn=3)
\tmodel.doesnt_match("breakfast cereal dinner lunch".split())
\tmodel.similarity('man', 'woman')
\t[ x for x in model.most_similar(positive=['sandy', 'haired'], 
\t\tnegative=['haired'], topn=100000) 
\t\tif '_haired' in x[0][-7:] and x[0].count('_') == 1]""")  #semantic_tests(model)