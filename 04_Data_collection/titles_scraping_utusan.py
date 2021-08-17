from datetime import date
from bs4 import BeautifulSoup
import requests
import pandas as pd 
import sys
import time

articles = []

if __name__ == '__main__':
    start = time.time()
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))

    section = sys.argv[1]
    category = sys.argv[2]
    begin = int(sys.argv[3])
    end = int(sys.argv[4])

    url = 'https://www.utusan.com.my/' + section + '/'
    xhr_url = 'https://www.utusan.com.my/?epic-ajax-request=epic-ne'

    with requests.Session() as session:
        session.headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        session.get(url)
        
        for page_no in range(begin, end):
            params = {'action': 'epic_module_ajax_epic_block_22',
            'data[current_page]': str(page_no),
            'data[attribute][header_type]': 'heading_6',
            'data[attribute][number_post][size]': '12',
            'data[attribute][pagination_number_post][size]': '6',
            'data[attribute][include_category]': category}

            response = session.post(xhr_url, data=params, headers={
                        "content-type": 'application/x-www-form-urlencoded',
                        "x-requested-With": "XMLHttpRequest",
                        "referer": url})
            
            soup = BeautifulSoup(response.json()['content'], 'html.parser')
            
            for div in soup.find_all("div" , class_ = "jeg_postblock_content"):
                title_link = div.find_all('a')[0]
                date = div.find_all('a')[1]
                articles.append([title_link.text, title_link['href'], date.text])
    
    # Save the data as csv 
    df = pd.DataFrame(articles)
    df.columns = ['title', 'link', 'date'] 
    df.to_csv('data/utusan/' + section + '_' + str(begin) + '_' + str(end) + '.csv', index=False, encoding='utf-8-sig')
    print('done', time.time()-start)
    