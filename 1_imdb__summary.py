# Arnab Sen Sharma (arnab-api)
# Lecturer, Department of CSE
# Shahjalal University of Science and Technology

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
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--no-sandbox')
        # chrome_options.add_argument('--disable-dev-shm-usage')

        browser = webdriver.Chrome(driver_path, chrome_options=chrome_options)
        browser.implicitly_wait(3)
    browser.get(url)
    browser.implicitly_wait(3)

    return browser


def performClick(element):
    driver.execute_script("arguments[0].click();", element)


def getSoupFromElement(element):
    html = element.get_attribute('innerHTML')
    soup = BeautifulSoup(html, 'html.parser')

    return soup

def getDictFromTxtArr(people_arr, is_array = True):
    key = None
    ret = {}
    for people in people_arr:
        if(len(people) <= 1):
            continue
        if(":" in people):
            key = people[0:-1]
            if(is_array):
                ret[key] = []
        else:
            if(is_array):
                ret[key].append(people)
            else:
                ret[key] = people
    return ret


def mergeDict(target_dict, dct):
    for key in dct:
        target_dict[key] = dct[key]
    return target_dict


def parseSingleMovieInfo(soup, debug = False):
    if(debug == True):
        print(soup.prettify())

    movie_info = {}

    elem = soup.find("h3")
    # print(elem.prettify())
    title_elem = elem.find('a')
    # print(title_elem.prettify())
    # print(title_elem.find(text = True).strip())
    # title = title_elem.string.strip()
    title = title_elem.find(text = True).strip()
    # print(title, title_elem['href'])
    print(" >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  parsing movie #####< {} >#####".format(title))

    movie_info["link"]  = title_elem['href']
    movie_info["title"] = title

    try:
        year_elem = elem.find("span", {"class": "lister-item-year"})
        year = year_elem.string.strip()
        # print(year)
        movie_info["year"]  = year
    except:
        print("This movie does not have <year> available")

    try:
        rating_elem = soup.find("div", {"class": "ratings-bar"})
        # print(rating_elem.strong.string.strip())
        movie_info["rating"] = rating_elem.strong.string.strip()
    except:
        print("This movie does not have <rating> available")

    try:
        meta_score_elem = soup.find("span", {"class": "metascore"})
        # print(meta_score_elem.string.strip())
        movie_info["meta_score"] = meta_score_elem.string.strip()
    except:
        print("This movie does not have meta score available")

    prr = soup.findAll("p", {"class": "text-muted"})
    # for elem in prr:
    #     print(elem)

    keys = ["certificate", "runtime", "genre"]

    meta_info = prr[0]
    for key in keys:
        elem = meta_info.find("span", {"class": key})
        if(elem == None):
            print("{} does not exist for this movie".format(key))
        else:
            # print(key, " :: ", elem.string.strip())
            movie_info[key] = elem.string.strip()
            if(key == "genre"):
                movie_info[key] = movie_info[key].split(", ")

    try:
        plot_elem = prr[1]
        # print(plot_elem.string.strip())
        # print(plot_elem.findAll(text=True))
        try:
            movie_info["plot"] = plot_elem.string.strip()
        except:
            plot_arr = plot_elem.findAll(text=True)
            movie_info["plot"] = " ".join(plot_arr)
    except:
        print("This movie does not have <plot> information available")

    try:
        prr = soup.find("p", {"class": ""})
        prr = prr.findAll(text=True)

        people_arr = []
        for txt in prr:
            people_arr.append(txt.strip())

        people_dict = getDictFromTxtArr(people_arr)
        # print(people_dict)
        movie_info = mergeDict(movie_info, people_dict)
    except:
        print("This movie does not have <people> information available")


    try:
        prr = soup.find("p", {"class": "sort-num_votes-visible"})
        prr = prr.findAll(text=True)
    
        vote_arr = []
        for txt in prr:
            vote_arr.append(txt.strip())

        vote_dict = getDictFromTxtArr(vote_arr, is_array=False)
        movie_info = mergeDict(movie_info, vote_dict)
    except:
        print("This movie does not have <vote> information available")

    # print(movie_info)

    return movie_info



def parseAllMoviesInPage(driver, frm, try_cnt = 0):
    time.sleep(2)
    driver.implicitly_wait(2)

    # if(True):
    try:
        movie_elem_arr = driver.find_elements_by_class_name("lister-item")
        print(len(movie_elem_arr))

        if(len(movie_elem_arr) == 0):
            print(".................... Maybe connection error :: trying again --- try < {} >".format(try_cnt+1))
            driver.refresh()
            return parseAllMoviesInPage(driver, try_cnt+1)

        movie_arr = []
        cnt = 0
        for movie_elem in movie_elem_arr:
            soup = getSoupFromElement(movie_elem)
            movie_info = parseSingleMovieInfo(soup)
            cnt += 1
            print(frm + cnt, ">>", movie_info)
            movie_arr.append(movie_info)
        
        return movie_arr
    
    except:
        print(".................... ====> Maybe connection error :: trying again --- try < {} >".format(try_cnt+1))
        driver.refresh()
        return parseAllMoviesInPage(driver, try_cnt+1)


######################################################################################################################
# url_root = "https://www.imdb.com/search/title/?adult=include&count=250"
"1832501 - 1832750 >> https://www.imdb.com/search/title/?adult=include&count=250&after=WzE4MzI3ODksInR0MjE0NjM3MiIsMTgzMjc1MV0%3D&ref_=adv_nxt"
url_root = "https://www.imdb.com/search/title/?adult=include&count=250&after=WzE4MzI3ODksInR0MjE0NjM3MiIsMTgzMjc1MV0%3D&ref_=adv_nxt"
save_path = "SUMMARY_DATA"
makeDirectory(save_path)
######################################################################################################################

driver = initialize(url_root)


############################
# frm = 1
frm = 1832501 + 250
rng = 250
cnt = 0
############################


pagelinks = []
while(True):
    print("\n\n\n ****************** parsing from {} to {} ****************** \n\n\n".format(frm, frm + rng - 1))
    
    movie_arr = parseAllMoviesInPage(driver, frm)
    # soup = getSoupFromElement(movie_elem_arr[48])
    # movie_info = parseSingleMovieInfo(soup, debug=True)
    # print(movie_info)

    with open(save_path + "/{} - {}.json".format(frm, frm+rng-1), "w") as f:
        json.dump(movie_arr, f)
        print("\n Saved movies {} to {}\n".format(frm, frm+rng-1))

    flag = True
    while(flag):
        try:
            next_button = driver.find_element_by_link_text("Next »")
            # next_button = driver.find_element_by_link_text("arnab")
            flag = False
        except:
            print("maybe the page did not load -- trying again")
            driver.refresh()
            time.sleep(2)
            flag = True

    print("{} - {}".format(frm, frm + rng - 1), end = " >> ")
    print(next_button.get_attribute("href"))
    pagelinks.append("{} - {} >> {}".format(frm, frm + rng - 1, next_button.get_attribute("href")))

    with open("links_4.json", "w") as f:
        json.dump(pagelinks, f)
    performClick(next_button)
    
    frm += 250

