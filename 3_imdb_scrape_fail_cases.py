from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.action_chains import ActionChains
import time
import json
import re
import os
import datetime

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
        print("creating browser for the first and last time")
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--no-sandbox')
        # chrome_options.add_argument('--disable-dev-shm-usage')

        browser = webdriver.Chrome(driver_path, chrome_options=chrome_options)
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
    # print(" >>>>>>>>>>>>>>>>>>>>>>>>> ")
    # print(cast_table.prettify())

    cast_elem_arr = cast_table.findAll("tr", {"class": "odd"}) + cast_table.findAll("tr", {"class": "even"})
    # print(len(cast_elem_arr))
    # print(cast_elem_arr[0].prettify())

    cast_and_character = []

    for cast_elem in cast_elem_arr:
        td_arr = cast_elem.findAll("td")
        if(len(td_arr) < 4):
            continue
        
        # print(td_arr[1].prettify())
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


    # print(cast_and_character)
    # print(len(cast_and_character))
    return cast_and_character

def checkvalidtext(txt):
    if(txt.isspace()):
        return False
    arr = ["|", "See more", "\u00bb", ","]
    if txt in arr:
        return False
    if txt.strip() in arr:
        return False
    return True


def filter(arr):
    ret = []
    attr = "#"
    for val in arr:
        if(checkvalidtext(val) == False):
            continue
        if(val[-1] == ":"):
            attr = val[0:-1]
            continue
        ret.append(val.strip())
    return attr, ret 

def parseDetailInfo(page_soup):
    detail_elem = page_soup.find("div", {
        'class': 'article',
        'id': "titleDetails"
    })
    divs = detail_elem.findAll("div")
    
    details = {}
    for div in divs:
        vrr = div.findAll()
        attr, value = filter(div.findAll(text=True))
        if(attr == "Official Sites" or attr == "#" or attr == "Color"):
            continue
        # print(attr, " >>>>>> ", value)
        details[attr] = value

    return details


def processOneMovie(movie_url, folder_path, driver, try_cnt = 0):

    # if(True):
    try:
        if(try_cnt == 0):
            driver = initialize(movie_url, driver)

        page_html = driver.page_source
        page_soup = BeautifulSoup(page_html, 'html.parser')

        # print(page_soup.prettify())

        query_result = page_soup.find("script", {"type": "application/ld+json"})
        # print(query_result.string)
        meta_data = json.loads(query_result.string)
        try:
            meta_data["cast_and_character"] = getCastInfo(page_soup)
        except:
            meta_data["cast_and_character"] = "Error loading cast information -- checked {}".format(datetime.datetime.now())
        
        meta_data['details'] = parseDetailInfo(page_soup)

        movie_id = meta_data["url"].split('/')[-2]
        movie_name = meta_data["name"]

        file_name = "{}__{}".format(movie_id, simplify_string(movie_name)) + ".json"
        # print(file_name)
        # print(meta_data)

        with open(folder_path + "/" + file_name, "w") as f:
            json.dump(meta_data, f)
            print("saved movie < {} > to < {} >".format(movie_name, file_name))

        return True
    
    except:
        if(try_cnt == 5):
            print("Error loading movie -- skip this")
            return False

        print("maybe temporary internet connection problem. trying again < {} >".format(try_cnt + 1))
        driver.refresh()
        time.sleep(2)
        return processOneMovie(movie_url, folder_path, driver, try_cnt+1)



#############################################################################################################
url_root = "https://www.imdb.com/"
save_path = "MOVIES"
summary_path = "IMDB_SUMMARY/SUMMARY_DATA"
frm = 100000 + 1
rng = 250
limit = 150000 # set it to -1 for all processing

#############################################################################################################

makeDirectory(save_path)
summary_files = sorted(os.listdir(summary_path))
driver = initialize(url_root)

print(summary_files)
# for summary in summary_files:

try:
    with open("fail_cases.json", "r") as f:
        fail_cases = json.load(f)
except:
    print("Could not find fail_cases.json -- initializing with empty folder")
    fail_cases = []


while(True):
    summary = "{} - {}.json".format(frm, frm+rng-1)

    if(summary not in summary_files):
        print("Could not fild summary file < {} >".format(summary))
        break


    print("Checking < {} >".format(summary))

    folder_name = summary.split('.')[0]
    folder_path = save_path + "/" + folder_name
    # makeDirectory(folder_path)

    with open(summary_path + "/" + summary) as f:
        movie_arr = json.load(f)
        # print(type(movie_arr))
        # print(movie_arr)
    process_cnt = 0

    st = 0
    # if(frm == 65251):
    #     st = 173

    for idx in range(st, len(movie_arr)):
        movie = movie_arr[idx]

        if(movie not in fail_cases):
            continue

        print("checking url {} to get movie {} -- folder path {}".format(movie["link"], movie["title"], folder_path))

        movie_url = url_root + movie["link"]
        success = processOneMovie(movie_url, folder_path, driver)

        if(success == True):
            print("!!! SUCCESSFULL !!! saving {} to {}".format(movie["title"], folder_path))
            while(movie in fail_cases):
                fail_cases.remove(movie)
            with open("fail_cases.json", "w") as f:
                json.dump(fail_cases, f)

        # process_cnt += 1
        # print(">>>>>>>>>>>>>>>>>>>>>>>>>> processed {} of {} --- of :: {}".format(st + process_cnt, len(movie_arr), summary))
    
    frm += rng

    if limit == -1:
        continue
    elif (frm > limit):
        break
 