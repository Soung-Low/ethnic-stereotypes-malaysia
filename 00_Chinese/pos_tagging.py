'''
This script contains the code to conduct part-of-speech tagging for Chinese texts. 
'''

import jieba
import jieba.posseg as pseg
import paddle
import pandas as pd
import pickle
import sys
import time
from multiprocessing import Pool

def get_word_by_pos(text, tag, paddle=False):
    '''Extract words from a text given a POS tag'''
    tokens = pseg.cut(text, use_paddle=paddle)
    words = [token for token, flag in tokens if flag == tag ]
    return words 

if __name__ == '__main__':
    file = sys.argv[1]
    tag = sys.argv[2]
    paddle = sys.argv[3] == 'True'

    if paddle == True:
        paddle.enable_static()
        jieba.enable_paddle()

    # Load dataframe that contains an 'article' column
    df = pickle.load(open(file, 'rb'))

    # Apply pos tag function on articles using multiprocessing 
    start = time.time()
    pool = Pool()
    data = pool.starmap(get_word_by_pos, [(article, tag, paddle) for article in df.article])
    data = [word for words in data for word in words]
    
    pool.close()
    pool.join()

    pickle.dump(data, open("data/pos_" + tag, "wb"))
    print("done", time.time()-start)
