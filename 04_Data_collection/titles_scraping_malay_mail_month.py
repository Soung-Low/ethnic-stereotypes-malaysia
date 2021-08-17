from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

import sys
import time
import pandas as pd 

# Define functions
def check_exists_by_xpath(xpath, timeout=5):
    '''Return a boolean that indicates the presence of an element given a xpath.'''
    try:
        WebDriverWait(driver, timeout=timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath)))
        return True
    except:
        return False

def check_clickable_by_xpath(xpath, timeout=3):
    '''Return a boolean that represents whether an element given a xpath is clickable.'''
    try:
        WebDriverWait(driver, timeout=timeout).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        return True
    except:
        return False

def scrape_titles_links(year_month):
    '''Return a list of titles and links for articles on present page.'''
    # Collect titles and urls of articles
    titles_links = []
    
    try:
        articles = WebDriverWait(driver, timeout=5).until(
            EC.presence_of_all_elements_located((By.XPATH, "//a[@class='py-2 d-block']"))
        ) # make sure all elements are loaded

        for a in articles:
            title = a.text
            link = a.get_attribute('href')
            titles_links.append([year_month, title, link])
    
    except: 
        # Pass if no articles were found
        #if driver.find_element_by_xpath("//div[@class='alert alert-warning']/p").text == 'No articles found.':
        print('No articles found.')

    return titles_links 

if __name__ == '__main__':
    start = time.time()
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))

    # Specify the section, the year, the month when running the script 
    section = str(sys.argv[1]) 
    year = str(sys.argv[2])
    month = str(sys.argv[3]) 

    # Open a browser 
    driver = webdriver.Chrome()
    titles_links = []
    driver.get('https://www.malaymail.com/news/' + section + '/' + year)

    # Click the consent button for collection of personal data
    consent_button = driver.find_element_by_xpath("//button[@class='fc-button fc-cta-consent fc-primary-button']")
    ActionChains(driver).click(consent_button).perform()

    # Select the specified year
    year_menu = Select(driver.find_element_by_id('inputYear'))
    year_menu.select_by_visible_text(year)
    
    # Identify drop down menu for months 
    month_menu = Select(driver.find_element_by_id('inputMonth')) 
    previous_len = len(titles_links)

    # Select month by text 
    month_menu.select_by_visible_text(month)
    
    # Click submit button 
    driver.find_element_by_xpath("//button[@type='submit']").click() 

    next_page = True 
    while next_page:
        # If next button is available 
        if check_clickable_by_xpath("//a[@class='page-link'][@rel='next']"):  
            # Collect titles and urls of articles on present page
            titles_links.extend(scrape_titles_links(year + '_' + month))

            # Click the next button when it's clickable
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[@class='page-link'][@rel='next']")))
            action = ActionChains(driver)
            action.click(next_button) 
            action.perform()

            # Navigate to the advertisement iframe if present
            if check_exists_by_xpath("//iframe[@id='aswift_1']"):
                print('advertisement identifed.')
                frame = driver.find_element_by_xpath("//iframe[@id='aswift_1']")
                driver.switch_to.frame(frame)
                print('driver switched to iframe.')

                if check_exists_by_xpath("//div/div[@id='dismiss-button']", 3):
                    # Ad type 1: close button on top right
                    driver.find_element_by_xpath(("//div/div[@id='dismiss-button']")).click()
                    print('advertisement closed.')
                    driver.switch_to.default_content()
                elif check_exists_by_xpath("//iframe[@id='ad_iframe']"):
                    # Ad type 2: close button within the ad 
                    # Switch to iframe inside iframe
                    frame = driver.find_element_by_xpath("//iframe[@id='ad_iframe']")
                    driver.switch_to.frame(frame)
                    print('driver switched to iframe inside iframe.')

                    # Click the close button 
                    try:
                        WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, "//div/div[@id='dismiss-button']"))).click()
                        #driver.find_element_by_xpath(("//div/div[@id='dismiss-button']")).click()
                        print('advertisement closed.')
                        driver.switch_to.default_content()
                    except:
                        pass
                else:
                    pass
            
            # Click the consent button for collection of personal data if present:
            if check_exists_by_xpath("//button[@class='fc-button fc-cta-consent fc-primary-button']"):               
                consent_button = driver.find_element_by_xpath("//button[@class='fc-button fc-cta-consent fc-primary-button']")
                ActionChains(driver).click(consent_button).perform()
        else:
            # Stop when there is no addtional page
            print(month, 'last page.')

            # Collect titles and urls of articles
            titles_links.extend(scrape_titles_links(year + '_' + month))
            print(month, 'No. of articles:', len(titles_links))

            next_page = False

    # Save the data as csv 
    df = pd.DataFrame(titles_links)
    df.columns = ['year_month', 'title', 'link'] 
    df.to_csv('data/malay_mail/' + section + '_' + year + '_' + month + '.csv', index=False, encoding='utf-8-sig')

    # Close the browser
    driver.quit()

    print("done", time.time()-start)