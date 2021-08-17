from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import pandas as pd 
import sys
import time 

# Define function 
def check_exists_by_xpath(xpath, timeout=2):
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
    timestamps = []
    articles = []

    # Open a browser
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)

    # Set the time a page can take to load
    driver.set_page_load_timeout(15) 

    # Collect information for each article given a link 
    for link in df['link']:   
        try:
            driver.get(link)
        except TimeoutException: 
            # Stop pending requests when taking longer than 20s to load 
            # driver.execute_script("window.stop();")
            print('Maximum time exceeded:', link)

        # Click the consent button for collection of personal data if present
        if check_exists_by_xpath("//button[@class='fc-button fc-cta-consent fc-primary-button']"):
            consent_button = driver.find_element_by_xpath("//button[@class='fc-button fc-cta-consent fc-primary-button']")
            actions = ActionChains(driver).click(consent_button)
            actions.perform()

        try:
            # Collect timestamp 
            timestamps.append(driver.find_element_by_xpath('//div[@class="byline"]/p').text)

            # Collect article 
            article = WebDriverWait(driver, 2).until(EC.presence_of_all_elements_located((By.XPATH, "//article/p")))
            article = ' '.join([text.text for text in article])
            articles.append(article)
        except:
            timestamps.append(None)
            articles.append(None)

    # Close the browser
    driver.quit()
    print('Number of articles scraped', str(len(articles)))

    # Save scraped articles 
    df['time'] = timestamps
    df['article'] = articles
    df.to_csv('data/malay_mail/' + file.split('.')[0] + '_complete.csv', index=False, encoding='utf-8-sig')

    print("done", time.time()-start)