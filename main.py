import re
import time
import requests
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from helpers import parse_page, yield_url

# beautiful soup used with pregenerated urls
# https://www.airbnb.com/s/Rethimnon--Greece/homes?pagination_search=true&items_offset=20&room_types%5B%5D=Entire%20home%2Fapt&room_types%5B%5D=Private%20room&room_types%5B%5D=Hotel%20room&search_type=filter_change

pages = []
months = ['july','august']
adults = 6
counter = 0    
max_offset = 300
offset_step = 20 # dont change

if __name__ == '__main__':

    for i in range(0,max_offset,offset_step):        
        
        # paginated urls
        base = yield_url(months,adults)
        url = base + f'&pagination_search=true&items_offset={str(i)}'
        try :
            page = requests.get(url)
            soup = BeautifulSoup(page.content, 'html.parser')
            pages.append(soup)
            counter += 1
            print(f'> parsed page {str(counter)}({round(((i+offset_step)/max_offset)*100,2)}%)')
        except Exception as e:
            print(f'error during : {url}' )

    # given a page (soup), parse all of its listings
    df_list = [parse_page(page) for page in pages]
    # concat individual dfs into a dataframe
    df = pd.concat(df_list).reset_index(drop=True)
    print(f'parsed df shape : {df.shape}')
    # add custom column to determine uniqueness of a listing
    df['unique_string'] = (df.title + df.reviews_price)
    print(f'"unique_string" distinct items : {df.unique_string.nunique()}')
    # drop columns based on custom column from above
    df.drop_duplicates(subset=['unique_string'],inplace=True)
    print(f'final df shape : {df.shape}')
    

df.to_clipboard()
df.shape

# ---------------------------------------------------------------------------------    
# ---------------------------------------------------------------------------------
# code to parse individual page
# selenium for traversing the site
# ---------------------------------------------------------------------------------    
# ---------------------------------------------------------------------------------

CHROMEDRIVER = '/home/takis/Desktop/sckool/chromedriver_linux64/chromedriver'
URL = 'https://www.airbnb.com/s/Rethimnon--Greece/homes'

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')

driver = webdriver.Chrome(CHROMEDRIVER)

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

for hurl in home_url_list:

    print(hurl)
    
    url = 'http://'+hurl
    # page = requests.get(url)
    # soup = BeautifulSoup(page.content, 'html.parser')

    current_listing = {}
    driver.get(url)
    time.sleep(2) # Let the user actually see something!
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2) # Let the user actually see something!
    
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
    boo = [x.text for x in soup.find('div',class_=parsing_dict['subtitle']).find_all('span') if x.text != ' · ']
    current_listing['subtitle'] = "-".join(boo)

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
    
    # cancellation policy
    # driver.find_elements_by_xpath("//*[contains(text(), 'Show more')]")[8].click()

    # map coordinates
    url_string = str(driver.page_source)
    p_lat = re.compile(r'"lat":([-0-9.]+),')
    p_lng = re.compile(r'"lng":([-0-9.]+),')
    try:
        lat = p_lat.findall(url_string)[0]
        lng = p_lng.findall(url_string)[0]
    except:
        lat = lon = -999
    current_listing['coordindates'] = (lat,lng)

    # calendar
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'lxml')
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

# driver.quit()

