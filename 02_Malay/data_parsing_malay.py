import os
import time
import pickle   
import io
import sys
import re
import pandas as pd

from io import StringIO
from multiprocessing import Pool
from pdfminer.high_level import extract_text

def pdf_to_text(file_name):
    '''Extract text from a pdf given its file name'''
    fp = open(file_name, 'rb')
    try:
        text = extract_text(file_name)

        # Remove irrelevant characters 
        text = text.replace('\n', ' ')
        text = text.replace('\x0c', ' ')
        text = text.replace('-- LAGI', ' ')
        text = text.replace('--LAGI', ' ')
        text = text.replace('© Bernama Library & Infolink Service ', ' ')
        text = text.strip()

        # Get title, date, and author 
        title = re.search(r"\b[0-9A-Z\s'‘’,:-]+\b", text)[0]

        if re.search(r'\|\s[0-9]{2}\/[0-9]{2}\/[0-9]{4}\s\|', text):
            date = re.search(r'\|\s[0-9]{2}\/[0-9]{2}\/[0-9]{4}\s\|', text)[0]
            date = date.strip('| ')
        else: 
            date = None

        if re.search(r'(Author:)[a-zA-Z\s\/]+\|', text):
            author = re.search(r'(Author:)[a-zA-Z\s\/]+\|', text)[0]
            text = text.split(author)[1]
            author = author.replace('Author:', '')
            author = author.strip('| ')
        else: 
            author = None

        # Remove pre-article information before the word '(BERNAMA)'
        if '(Bernama)' in text:
            text = text.split('(Bernama)')[1]
        elif '( B e r n a m a )' in text:
            text = text.split('( B e r n a m a )')[1]
        else:
            pass 

        # Remove post-article information
        if re.search('--[\s]*(BERNAMA)', text):
            text = text.split(re.search('--[\s]*(BERNAMA)', text)[0])[0]  
        text = text.strip(' -–')  

        return (title, date, author, text)

    except:
        return (None, None, None, None)      

if __name__ == '__main__':
    start = time.time()
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))

    folder = sys.argv[1]
    os.chdir('../data/bernama/articles/' + folder)
    files = os.listdir()

    # Create lists to store information of articles 
    titles = []
    dates = []
    authors = []
    articles = []

    pool = Pool()
    data = pool.map(pdf_to_text, files)

    for article in data:
        titles.append(article[0])
        dates.append(article[1])
        authors.append(article[2])
        articles.append(article[3])

    # Create a dataframe 
    df = pd.DataFrame({'title': titles, 'date': dates, 'author': authors, 'article': articles})
    pickle.dump(df, open("../../pickle/article_" + folder, "wb"))
    
    pool.close()
    pool.join()

    print("done", time.time()-start)
