
# coding: utf-8

# In[119]:


from collections import Counter, defaultdict


# In[120]:


src = open('./pat.src.txt', 'r', encoding='utf8').read().split('\n\n')
tgt = open('./pat.tgt.txt', 'r', encoding='utf8').read().split('\n\n')


# In[121]:


lang_model = defaultdict(Counter)
channel_model = defaultdict(Counter)

for bef, aft in zip(src, tgt):
    bef_ptn_group = [(each.split('\t')[0], each.split('\t')[1]) for each in bef.strip().split('\n')[1:]]
    aft_ptn_group = [(each.split('\t')[0], each.split('\t')[1]) for each in aft.strip().split('\n')[1:]]
    for b_head, b_ptn in bef_ptn_group:
        for a_head, a_ptn in aft_ptn_group:
            lang_model[a_head][a_ptn] += 1
            if b_head == a_head and b_ptn != a_ptn: # 同 head 不同 pattern
                channel_model[b_ptn][a_ptn] += 1


# In[122]:


src = open('./pat.test.src.txt', 'r', encoding='utf8').read().split('\n\n')
answers = open('./ef_test.ref.txt', 'r', encoding='utf8').read().split('\n')


# In[123]:


for i, bef in enumerate(src):
    sent, edits = bef.strip().split('\n', maxsplit=1)
    print(sent)
    for edit in edits.split('\n'):
        head, pattern, ngram = edit.split('\t')
        # if head not in ['DISCUSS', 'ANSWER', 'APPLY', 'EXPLAIN']: continue
        
        chances = [ (aft_ptn, channel_model[pattern][aft_ptn] / sum(channel_model[pattern].values())
                  * lang_model[head][aft_ptn] / sum(lang_model[head].values())) for aft_ptn in channel_model[pattern]]
        print()
        print(head + '\t' + pattern, '->', max(chances, key=lambda x: x[1]))
    print()
    print("answer:", answers[i].split('\t', maxsplit=1)[1])
    print("="*50)

