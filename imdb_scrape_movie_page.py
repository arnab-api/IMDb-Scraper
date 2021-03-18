from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.action_chains import ActionChains
import time
import json
import re
import os

###########################################################################
driver_path = "/home/arnab/Codes/00_Libs/chromedriver_linux64/chromedriver"
###########################################################################

def simplify_string(inp):
    inp = inp.lower().strip()
    inp = re.sub(r'[^A-Za-z0-9]', '_', inp)

    return inp

def makeDirectory(path):
    print("creating directory " + path)
    try:
        os.mkdir(path)
    except FileExistsError:
        pass

def initialize(url, browser=None):
    if(browser == None):
        browser = webdriver.Chrome(driver_path)
        browser.implicitly_wait(3)
    browser.get(url)
    browser.implicitly_wait(3)

    return browser


def performClick(driver, element):
    driver.execute_script("arguments[0].click();", element)


def getSoupFromElement(element):
    html = element.get_attribute('innerHTML')
    soup = BeautifulSoup(html, 'html.parser')
    return soup

movie_url = "https://www.imdb.com/title/tt6257970/?ref_=adv_li_tt"

driver = initialize(movie_url)
time.sleep(2)
driver.implicitly_wait(2)

page_html = driver.page_source
page_soup = BeautifulSoup(page_html, 'html.parser')

# print(page_soup.prettify())

query_result = page_soup.find("script", {"type": "application/ld+json"})
# print(query_result.string)
meta_data = json.loads(query_result.string)

movie_id = meta_data["url"].split('/')[-2]
movie_name = meta_data["name"]

file_name = "{}__{}".format(movie_id, simplify_string(movie_name))
print(file_name)
print(meta_data)