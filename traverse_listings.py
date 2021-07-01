
import re
import time
import requests
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from helpers import parse_page, yield_url

# ---------------------------------------------------------------------------------    
# ---------------------------------------------------------------------------------
# code to parse individual page
# selenium for traversing the site
# ---------------------------------------------------------------------------------    
# ---------------------------------------------------------------------------------

CHROMEDRIVER = '/home/takis/Desktop/sckool/chromedriver_linux64/chromedriver'
URL = 'https://www.airbnb.com/s/Rethimnon--Greece/homes'

# options = webdriver.ChromeOptions()
# options.add_argument('--ignore-certificate-errors')
# options.add_argument('--incognito')
# options.add_argument('--headless')

driver = webdriver.Chrome(CHROMEDRIVER)

df = pd.read_csv('data/listings.csv')
home_url_list = df.functional_url.tolist()

parsing_dict = {'title':'_xcsyj0',
                'subtitle': '_tqmy57',
                'about_place_open':'/html/body/div[4]/div/div[1]/div/div/div/div/div[1]/main/div/div[1]/div[3]/div[1]/div/div[3]/div/div[2]/div[2]/div/button',
                'about_place_parse':'/html/body/div[10]/section/div/div/div/div/div/div/div/div/div[2]/div/div/section',
                'about_place_close':'/html/body/div[10]/section/div/div/div/div/div/div/div/div/div[1]/div/button',
                'amenities_open':'/html/body/div[4]/div/div[1]/div/div/div/div/div[1]/main/div/div[1]/div[3]/div[1]/div/div[5]/div/div[2]/div[4]/a',
                'amenities_close':'/html/body/div[10]/section/div/div/div[1]/button',
                'about_location_open':'/html/body/div[4]/div/div[1]/div/div/div/div/div[1]/main/div/div[1]/div[5]/div/div/div/div[2]/div[4]/a',
                'about_location_parse':'/html/body/div[10]/section/div/div/div[3]/div/div[1]/div[2]/div/span/div/span',
                'about_location_close':'/html/body/div[10]/section/div/div/div[1]/button',
                'house_rules_open':'/html/body/div[4]/div/div[1]/div/div/div/div/div[1]/main/div/div[1]/div[7]/div/div/div/div[2]/div/div[2]/div[1]/div/div/div[7]/a',
                'house_rules_parse':'/html/body/div[10]/section/div/div/div[3]/div/div/section',
                'house_rules_close':'/html/body/div[10]/section/div/div/div[1]/button',
                'calendar':'_cvkwaj',
                'price_xpath':'/html/body/div[4]/div/div[1]/div/div/div/div/div[1]/main/div/div[1]/div[3]/div[2]/div/div/div[1]/div/div/div/div/div/div[1]/div[1]/div[1]/div/div/div/div/span[1]',
                'rating_xpath':'/html/body/div[4]/div/div[1]/div/div/div/div/div[1]/main/div/div[1]/div[3]/div[2]/div/div/div[1]/div/div/div/div/div/div[1]/div[1]/div[2]/span/span[2]',
                'review_xpath':'/html/body/div[4]/div/div[1]/div/div/div/div/div[1]/main/div/div[1]/div[3]/div[2]/div/div/div[1]/div/div/div/div/div/div[1]/div[1]/div[2]/span/a/span'}

listing_details = {}

# len(home_url_list)

for hurl in home_url_list[:5]:

    # hurl = 'airbnb.com/rooms/23030014?adults=4&children=0&infants=0&check_in=2021-07-09&check_out=2021-07-11&previous_page_section_name=1000&translate_ugc=false&federated_search_id=114a3f24-d12e-45ff-9933-1aff00c022b8'
    # print(hurl)
    
    url = 'http://'+hurl
    # page = requests.get(url)
    # soup = BeautifulSoup(page.content, 'html.parser')

    current_listing = {}
    driver.get(url)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'lxml')
    time.sleep(3) # Let the user actually see something!
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3) # Let the user actually see something!
    
    # price
    try:
        current_listing['price'] = driver.find_element_by_xpath(parsing_dict['price_xpath']).text
    except:
        current_listing['price'] = 'NA'
    
    # rating
    try:
        current_listing['rating'] = driver.find_element_by_xpath(parsing_dict['rating_xpath']).text
    except:
        current_listing['rating'] = 'NA'
    
    # reviews
    try:
        current_listing['reviews'] = driver.find_element_by_xpath(parsing_dict['review_xpath']).text
    except:
        current_listing['reviews'] = 'NA'
    
    # title
    try:
        current_listing['title'] = soup.find('div',class_=parsing_dict['title']).text
    except:
        current_listing['title'] = 'NA'

    # subtitle
    try:
        boo = [x.text for x in soup.find('div',class_=parsing_dict['subtitle']).find_all('span') if x.text != ' · ']
        current_listing['subtitle'] = "-".join(boo)
    except:
        current_listing['subtitle'] = 'NA'
        
    # about place - OR in the url &modal=DESCRIPTION
    try:
        # driver.find_element_by_xpath(parsing_dict['about_place_open']).click()
        driver.find_elements_by_xpath("//*[contains(text(), 'Show more')]")[0].click()
        # current_listing['about_place'] = driver.find_element_by_xpath(parsing_dict['about_place_parse']).text.replace('\n',' ')
        current_listing['about_place'] = BeautifulSoup(driver.page_source,'lxml').text.replace('\n',' ')
        # driver.find_element_by_xpath(parsing_dict['about_place_close']).click()
        webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
    except:
        current_listing['about_place'] = 'NA'

    # amenities /room/1928432/amenities
    try:
        # driver.find_element_by_xpath(parsing_dict['amenities_open']).click()
        driver.find_elements_by_xpath("//*[contains(text(), 'Show all')]")[1].click()
        soo = [x.text.replace('\n',' ') for x in driver.find_elements_by_class_name('_aujnou')]
        current_listing['amenities'] = " ".join(soo)
        # driver.find_element_by_xpath(parsing_dict['amenities_close']).click()
        webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
    except:
        current_listing['amenities'] = 'NA'
        
    # # about_location
    # driver.find_element_by_xpath(parsing_dict['about_location_open']).click()
    # driver.find_elements_by_xpath("//*[contains(text(), 'Show more')]")[4].click()
    # # current_listing['about_location'] = driver.find_element_by_xpath(parsing_dict['about_location_parse']).text
    # current_listing['about_location'] = BeautifulSoup(driver.page_source,'lxml').text.replace('\n',' ')
    # # driver.find_element_by_xpath(parsing_dict['about_location_close']).click()
    # webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()

    # # house_rules
    # driver.find_element_by_xpath(parsing_dict['house_rules_open']).click()
    # current_listing['house_rules'] = driver.find_element_by_xpath(parsing_dict['house_rules_parse']).text.replace('\n',' ')
    # current_listing['house_rules'] = BeautifulSoup(driver.page_source,'lxml').text.replace('\n',' ')
    # driver.find_element_by_xpath(parsing_dict['house_rules_close']).click()
    # webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()    
    
    # cancellation policy - /rooms/23030014/cancellation-policy?
    try:
        driver.find_elements_by_xpath("//*[contains(text(), 'Show more')]")[8].click()
        xpath_cp = '/html/body/div[10]/section/div/div/div[3]/div/div/div/div/section/div'
        current_listing['cancellation_policy'] = driver.find_element_by_xpath(xpath_cp).text.replace('\n',' ')
    except:
        current_listing['cancellation_policy'] = ' NA'

    # map coordinates
    url_string = str(page_source)
    p_lat = re.compile(r'"lat":([-0-9.]+),')
    p_lng = re.compile(r'"lng":([-0-9.]+),')
    try:
        lat = p_lat.findall(url_string)[0]
        lng = p_lng.findall(url_string)[0]
        current_listing['coordindates'] = (lat,lng)
    except:
        current_listing['coordindates'] = (-999,-999)
    
    # calendar
    oto = soup.find_all('table', parsing_dict['calendar'])
    current_month = datetime.now().month

    if len(oto)>0:
        calendar = {}
        # current_month
        for dd in oto[0].find_all('td'):
            if len(dd.text)!=0:
                date = dd.text 
                try :
                    availability = dd.find('div')['data-is-day-blocked']
                except :
                    availability = 'Na'
                # print(f'{date}-{availability}')
                calendar[f'month_{str(current_month)}_day_{date}'] = availability

        # next_month
        for dd in oto[2].find_all('td'):
            if len(dd.text)!=0:
                date = dd.text 
                try :
                    availability = dd.find('div')['data-is-day-blocked']
                except :
                    availability = 'Na'
                # print(f'{date}-{availability}')
                calendar[f'month_{str(current_month+1)}_day_{date}'] = availability

        bookings = pd.Series(calendar)
        current_listing['bookings'] = bookings
        current_listing['availability_rate'] = (bookings[bookings=='true'].shape[0]/bookings.shape[0])
    else:
        current_listing['bookings'] = None
        current_listing['availability_rate'] = None

    listing_details[hurl] = current_listing
    
dt = pd.DataFrame().from_dict(listing_details,orient='index').sort_values(by=['availability_rate'])
print(f'dt.shape:{dt.shape}')
dt.tail(20)
dt.to_clipboard()

driver.quit()

