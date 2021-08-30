import pandas as pd 

def count_word(word, tokens):
    '''Get frequencies of a word in a list.'''
    return tokens.count(word)

def get_freq_by_year(words, data, normalized=False):
    '''Count the frequency of each word in each year given a list and a dataframe. 
    
    Args:
        words(list): a list containing words of interest.
        data(pd.DataFrame): a dataframe with 'tokens' and 'date' columns.
        normalized(bool): normalize the frequency by total words in each year if True. 
        
    Return:
        a dataframe containing the frequency for each word in each year.
    '''
    years = data.date.dt.year.unique()
    dict_word_count = {word:[] for word in words}
    
    for word in words:
        for year in years:
            count = data.loc[data.date.dt.year == year, 'tokens'].apply(lambda tokens: count_word(word, tokens)).sum()
            if normalized == True:
                total = data.loc[data.date.dt.year == year, 'no_tokens'].sum()
                count = count/total
                
            dict_word_count[word].append(count)
    
    df = pd.DataFrame(dict_word_count)
    df.set_index(years, inplace=True)
    
    return df

def get_close_word(noun, models, n=20):
    '''Get top n words closest to a noun by year in trained embeddings.

    Args:
        noun (str): a string of the target noun.
        models (dict): a dictionary with keys = year, values = embeddings.
        n (int): desired number of closest words

    Return:
        a dataframe containing top n words closest to the given noun in each year.
    '''
    words = []

    for year in models:
        if noun in models[year].wv.vocab:
            word, dist = zip(*models[year].wv.most_similar(noun, topn=n))
            words.append(pd.Series(data=word, name=year))
        else:
            continue
            
    return pd.DataFrame(words).sort_index()

def verify_word_occurrence(word, models):
    '''Return True if the given word exists in every model (every year).'''
    occur = True

    for year in models:
        if word in models[year].wv.vocab:
            continue
        else:
            occur = False
            
    return occur

def filter_word_by_occurrence(words, models):
    '''Filter out words that do not exist in every model (every year). '''
    return [word for word in words if verify_word_occurrence(word, models)]

def get_close_adj(words, models, adjs, n=1000):
    '''Get adjectives that are closest to provided words in word embeddings. 
    This is for manual selection of adjectives that are for ethnic groups. 
    
    Args: 
        words (list): a list of words representing each ethnic group.
        models (dict): a dictionary with keys = year, values = embeddings,
        adjs (list): a list of words that contains adjectives (e.g. from POS tagging).
        n (int): desired number of closest adjectives. 
    
    Return:
        a dictionary with keys = given words, values = closest adjectives to each word. 
    '''
    dict_adjs = {word:[] for word in words}
    
    for word in words:
        for year in models:
            if word in models[year].wv.vocab:
                top_adjs = [adj[0] for adj in models[year].wv.most_similar(word, topn=n)]
                dict_adjs[word].extend([adj for adj in top_adjs if adj in adjs])
    
    dict_adjs = {key: set(values) for key, values in dict_adjs.items()}
    return dict_adjs

def get_close_adj_by_year(noun, models, adjs, n=20):
    '''Get top n adjectives closest to a noun by year in trained embeddings.

    Args: 
        noun (str): the target noun. 
        models (dict): a dictionary with keys = year, values = embeddings,
        adjs (list): a list of words that contains adjectives (e.g. from POS tagging).
        n (int): desired number of closest adjectives. 

    Return:
        a dataframe containing top n adjectives closest to the given noun in each year.
    '''
    words = []

    for year in models:
        word, dist = zip(*models[year].wv.most_similar(noun, topn=n*100)) # get n*100 words because of the following filtering
        word = [w for w in word if w in adjs] # make sure words are in the given adjectives list 
        if len(word) < n:
            word.extend([None]*(n-len(word)))
        else:
            word = word[:n]
        words.append(pd.Series(data=word, name=year))

    return pd.DataFrame(words).sort_index()

def get_average_distance(vec1, vec2, embeddings):
    '''Return the average cosine distance between two lists of vectors.'''
    cosine_dist = [1-embeddings.wv.similarity(x, y) for x in vec1 for y in vec2]
    return sum(cosine_dist)/len(cosine_dist)

def get_average_sim(vec1, vec2, embeddings):
    '''Return the average cosine similarity between two lists of vectors.'''
    cosine_sim = [embeddings.wv.similarity(x, y) for x in vec1 for y in vec2]
    return sum(cosine_sim)/len(cosine_sim)