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

def processPageAnchor(anchorElem):
    url = anchorElem['href']
    text = anchorElem.find(text=True).strip()
    return url, text

def getCastInfo(page_soup):
    cast_table = page_soup.find("table", {"class": "cast_list"})
    print(" >>>>>>>>>>>>>>>>>>>>>>>>> ")
    print(cast_table.prettify())

    cast_elem_arr = cast_table.findAll("tr", {"class": "odd"}) + cast_table.findAll("tr", {"class": "even"})
    print(len(cast_elem_arr))
    # print(cast_elem_arr[0].prettify())

    cast_and_character = []

    for cast_elem in cast_elem_arr:
        td_arr = cast_elem.findAll("td")
        if(len(td_arr) < 4):
            continue
        
        print("#################$$$$$$$$$$$$$$$$$$$$$")
        print(cast_elem.prettify())

        actor_elem = td_arr[1]


        actor_anchor = actor_elem.find("a")
        actor_url, actor_name = processPageAnchor(actor_anchor)
        actor_info = {
            "@type" : "Person",
            "url"   : actor_url,
            "name"  : actor_name
        }
        # print(actor_info)

        # print(td_arr[3].prettify())
        character_elem = td_arr[3]
        character_info = []
        character_anchor_arr = character_elem.findAll('a')
        for character_anchor in character_anchor_arr:
            character_url, character_name = processPageAnchor(character_anchor)
            character_info.append({
                "url"   : character_url,
                "name"  : character_name
            })

        # print(character_info)

        cast_and_character.append({
            "actor"                     : actor_info,
            "character_and_episodes"    : character_info
        })

        # break


    # print(cast_and_character)
    # print(len(cast_and_character))
    return cast_and_character



movie_url = "https://www.imdb.com//title/tt13650480/?ref_=adv_li_tt"


driver = initialize(movie_url)
time.sleep(2)
driver.implicitly_wait(2)

page_html = driver.page_source
page_soup = BeautifulSoup(page_html, 'html.parser')

print(page_soup.prettify())

query_result = page_soup.find("script", {"type": "application/ld+json"})
# print(query_result.string)
meta_data = json.loads(query_result.string)

movie_id = meta_data["url"].split('/')[-2]
movie_name = meta_data["name"]

file_name = "{}__{}".format(movie_id, simplify_string(movie_name))
print(" >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> ")
print(file_name)
print(json.dumps(meta_data, indent=4))


try:
    meta_data["cast_and_character"] = getCastInfo(page_soup)
except:
    print("problem loading cast information")

print(meta_data)
json_pretty = json.dumps(meta_data, indent=4)
print(json_pretty)