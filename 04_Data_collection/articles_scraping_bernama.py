from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import re
import pandas as pd
import sys
import time

if __name__ == '__main__':
    start_time = time.time()
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))

    start = int(sys.argv[1])
    end = int(sys.argv[2])

    options = webdriver.ChromeOptions()
    options.add_experimental_option('prefs', {
        "download.default_directory": 'C:\\Users\\user\\Dropbox\\0_MY498_Dissertation\\04_Codes\\data\\bernama\\articles', #Change default directory for downloads
        "download.prompt_for_download": False, # To auto download the file
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True  #It will not show PDF directly in chrome
    })

    url = 'http://blis.bernama.com/index.php?mod=articles&opt=la&cid=1'
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    input_name = driver.find_element_by_id("txt_username")
    input_name.send_keys("Upustaka02")

    input_pw = driver.find_element_by_xpath("//input[@type='password']")
    input_pw.send_keys("Upustaka02")

    button_submit = driver.find_element_by_xpath("//button[@type='submit']")
    ActionChains(driver).click(button_submit).perform()
    titles = []
    n = 1

    while n <= end: 
        # Only scrape specified pages
        if n >= start:
            info = WebDriverWait(driver, timeout=10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//td")))
            info = [title.text for title in info if title.text]
            info = [re.split('\n|\s\|\s', title.rstrip('|')) for title in info]
            titles.extend(info)

            # Wait until previous rows get stale
            wait = WebDriverWait(driver, timeout=10)
            wait.until(EC.staleness_of(rows)) 

            rows = WebDriverWait(driver, timeout=10, ignored_exceptions=StaleElementReferenceException).until(
                EC.presence_of_all_elements_located((By.XPATH, "//tbody/tr[@role='row']")))
            
            for row in rows:
                # Click the view button to show articles' content
                button_view = row.find_element_by_xpath(".//td[2]/b/a[@class='view_article']")
                action = ActionChains(driver).click(button_view)
                action.pause(1)
                action.perform()
                
                # Click the download button to download pdf
                button_download = WebDriverWait(driver, timeout=10).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[@onclick='javascript: fn_go_download()']")))
                action = ActionChains(driver).click(button_download)
                action.pause(1)
                action.perform()
                
                # Click the close button to close the window
                button_close = WebDriverWait(driver, timeout=10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@class='btn btn-default close-modal']")))
                action = ActionChains(driver).move_to_element(button_close).click()
                action.pause(1)
                action.perform()
        
        rows = WebDriverWait(driver, timeout=10, ignored_exceptions=StaleElementReferenceException).until(
            EC.presence_of_element_located((By.XPATH, "//tbody/tr[@role='row']")))

        # Navigate to the next page
        n += 1
        button_next = WebDriverWait(driver, timeout=10).until(
            EC.element_to_be_clickable((By.XPATH, "//li[@class='paginate_button next']/a")))
        action = ActionChains(driver).click(button_next)
        action.pause(1)
        action.perform()

        
    df = pd.DataFrame(titles)
    df.columns = ['title', 'category', 'date', 'author']

    time.sleep(3)
    button_logout = driver.find_element_by_xpath("//a[@title='Logout']")
    ActionChains(driver).click(button_logout).perform()

    df.to_csv('data/bernama/berita_dalam_negeri_' + str(start) + '_' + str(end) + '.csv', index=False, encoding='utf-8-sig')
    print("done", time.time()-start_time)