from selenium import webdriver

import sys
import time
import pandas as pd 

if __name__ == '__main__':
    start = time.time()

    # Specify the number of pages 
    pages = int(sys.argv[1])

    # Open a browser 
    driver = webdriver.Chrome()
    titles_links = []

    # Iterate through every page to get titles and links of articles 
    for i in range(1, pages+1):
        driver.get('https://www.chinapress.com.my/category/%E6%97%B6%E4%BA%8B/page/' + str(i))

        for article in driver.find_elements_by_xpath("//div[@class='category_page_post_content']/a"):
            title = article.text
            link = article.get_attribute('href')
            titles_links.append([title, link])

        time.sleep(1)

    # Save the data as csv 
    df = pd.DataFrame(titles_links)
    df.columns = ['title', 'link'] 
    df.to_csv('data/china_press/国内_时事.csv', index=False, encoding='utf-8-sig')

    # Close the browser
    driver.quit()
    print("done", time.time()-start)