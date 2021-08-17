from selenium import webdriver
from selenium.common.exceptions import TimeoutException

import pandas as pd 
import sys
import time 

if __name__ == '__main__':
    start = time.time()

    # Specify the csv file that contains the links for articles and the beginning and ending indices of articles 
    file = str(sys.argv[1])
    begin = int(sys.argv[2])
    end = int(sys.argv[3])
    df = pd.read_csv('data/china_press/' + file + '.csv')
    df = df.iloc[begin:end, ]
    print('Number of articles:', str(len(range(begin, end))))

    # Create lists to store information of articles
    dates = []
    views = []
    texts = []

    # Open a browser
    driver = webdriver.Chrome()

    # Collect information for each article given a link
    for link in df['link']:
        try:
            driver.get(link)
        except TimeoutException:
            # Stop pending requests when taking longer than 20s to load 
            driver.execute_script("window.stop();")
            print('Maximum time exceeded:', link)
        
        try:
            date = driver.find_element_by_xpath("//time[@class='entry-date published']").text
            view = driver.find_element_by_xpath("//span[contains(@class, 'count_view')]").text
            text = ''.join([paragraph.text for paragraph in driver.find_elements_by_xpath("//div[@class='entry-content clearfix']/p")])

            dates.append(date)
            views.append(view)
            texts.append(text)
        except:
            dates.append(None)
            views.append(None)
            texts.append(None)


    # Close the browser
    driver.quit()
    print('Number of articles scraped', str(len(texts)))

    # Save scraped articles 
    df['date'] = dates
    df['view'] = views
    df['article'] = texts
    df.to_csv('data/china_press/' + file + '_' + str(begin) + '_' + str(end) + '_complete.csv', index=False, encoding='utf-8-sig')

    print("done", time.time()-start)