from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.common.exceptions import TimeoutException

import pandas as pd 
import sys
import time 

# Define function 
def check_exists_by_xpath(xpath, timeout=5):
    '''Return a boolean that indicates the presence of an element given a xpath.'''
    try:
        WebDriverWait(driver, timeout=timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath)))
        return True
    except:
        return False


if __name__ == '__main__':
    start = time.time()
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))

    # Specify the the csv file that contains the links for articles 
    file = str(sys.argv[1])
    df = pd.read_csv('data/malay_mail/' + file)
    print('Number of articles:', str(df.shape[0]))

    # Create lists to store information of articles
    authors = []
    timestamps = []
    articles = []

    # Open a browser
    driver = webdriver.Chrome()

    # Set the time a page can take to load
    driver.set_page_load_timeout(20) 

    # Collect information for each article given a link 
    for link in df['link']:   
        # time.sleep(3) # wait 3 seconds before navigating to a new page
        try:
            driver.get(link)
        except TimeoutException: 
            # Stop pending requests when taking longer than 20s to load 
            driver.execute_script("window.stop();")
            print('Maximum time exceeded:', link)

        # Click the consent button for collection of personal data if present
        if check_exists_by_xpath("//button[@class='fc-button fc-cta-consent fc-primary-button']"):
            consent_button = driver.find_element_by_xpath("//button[@class='fc-button fc-cta-consent fc-primary-button']")
            ActionChains(driver).click(consent_button).perform()

        # Collect author and timestamp 
        author_time = [text.text for text in driver.find_elements_by_xpath('//div[@class="byline"]/p')]
        if len(author_time) == 2:
            timestamps.append(author_time[0])
            authors.append(author_time[1])
        # Case when author is not present
        elif len(author_time) == 1:
            timestamps.append(author_time[0])
            authors.append('None')

        # Collect article 
        article = ' '.join([text.text for text in driver.find_elements_by_xpath('//article/p')])
        articles.append(article)

    # Close the browser
    driver.quit()
    print('Number of articles scraped', str(len(articles)))

    # Save scraped articles 
    df['author'] = authors
    df['article'] = articles
    df.to_csv('data/malay_mail/' + file.split('.')[0] + '_complete.csv', index=False, encoding='utf-8-sig')

    print("done", time.time()-start)