import re
import time
import requests
import pandas as pd
from datetime import datetime
from selenium import webdriver
from bs4 import BeautifulSoup
from helpers import parse_page

# beautiful soup used with pregenerated urls
# https://www.airbnb.com/s/Rethimnon--Greece/homes?pagination_search=true&items_offset=20&room_types%5B%5D=Entire%20home%2Fapt&room_types%5B%5D=Private%20room&room_types%5B%5D=Hotel%20room&search_type=filter_change
    
max_offset = 300
offset_step = 20 # dont change
pages = []
counter = 0

if __name__ == '__main__':

    for i in range(0,max_offset+offset_step,offset_step):
        
        url = f'https://www.airbnb.com/s/Rethimnon--Greece/homes?pagination_search=true&items_offset={str(i)}&room_types%5B%5D=Entire%20home%2Fapt&room_types%5B%5D=Private%20room&room_types%5B%5D=Hotel%20room&search_type=filter_change'
        
        try :
            page = requests.get(url)
            soup = BeautifulSoup(page.content, 'html.parser')
            pages.append(soup)
            counter += 1
            print(f'> parsed page {str(i)}')
        except Exception as e:
            print(f'error during : {url}' )
        
    print(f'parsed pages counter : {str(counter)}')
    print(f'parsed pages list length : {len(pages)}')

    # given a page (soup), parse all of its listings
    df_list = [parse_page(page) for page in pages]
    # concat individual dfs into a dataframe
    df = pd.concat(df_list).reset_index(drop=True)
    print(f'parsed df shape : {df.shape}')
    # add custom column to determine uniqueness of a listing
    df['unique_string'] = (df.title + df.reviews)
    print(f'"unique_string" distinct items : {df.unique_string.nunique()}')
    # drop columns based on custom column from above
    df.drop_duplicates(subset=['unique_string'],inplace=True)
    print(f'final df shape : {df.shape}')
    
    
# code to parse individual page

# selenium for traversing the site
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
                'about_host':'//*[@id="site-content"]/div/div[1]/div[3]/div[1]/div/div[4]/div/div[2]/div/div[3]',
                'open_about_host':'//*[@id="site-content"]/div/div[1]/div[3]/div[1]/div/div[4]/div/div[2]/div[3]/div/button',
                'close_about_host':'//*[@id="decs_root"]/div[10]/section/div/div/div/div/div/div/div/div/div[1]/div/button',
                'open_amenities':'//*[@id="site-content"]/div/div[1]/div[3]/div[1]/div/div[6]/div/div[2]/div[4]/a',
                'close_amenities':'/html/body/div[11]/section/div/div/div[1]/button',
                'about_location':'//*[@id="site-content"]/div/div[1]/div[5]/div/div/div/div[2]/div[4]/a/span/span[1]',
                'house_rules':'//*[@id="site-content"]/div/div[1]/div[7]/div/div/div/div[2]/div/div/div[2]/div[1]/div/div',
                'calendar':'_cvkwaj'}

listing_details = {}

for hurl in home_url_list[:2]:

    print(hurl)
    
    url = 'http://'+hurl
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    driver.get(url)
    time.sleep(2) # Let the user actually see something!

    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'lxml')
    current_listing = {}
    
    # title
    current_listing['title'] = soup.find('div',class_=parsing_dict['title']).text

    # subtitle
    boo = [x.text for x in soup.find('div',class_=parsing_dict['subtitle']).find_all('span') if x.text != ' · ']
    current_listing['subtitle'] = "-".join(boo)

    # # about_host
    # bar = driver.find_element_by_xpath(parsing_dict['about_host'])
    # bar.text

    # # about_host_clickable
    # driver.find_element_by_xpath(parsing_dict['open_about_host']).click()
    # zoo = [x.text.replace('\n',' ') for x in driver.find_elements_by_xpath('/html/body/div[10]/section/div/div/div/div/div/div/div/div/div[2]/div/div')]
    # current_listing['about_host'] = " ".join(zoo)
    # driver.find_element_by_xpath(parsing_dict['close_about_host']).click()

    # amenities
    driver.find_element_by_xpath(parsing_dict['open_amenities']).click()
    time.sleep(2)
    soo = [x.text.replace('\n',' ') for x in driver.find_elements_by_class_name('_aujnou')]
    current_listing['amenities'] = " ".join(soo)
    driver.find_element_by_xpath(parsing_dict['close_amenities']).click()

    # about_location
    current_listing['about_location'] = driver.find_element_by_xpath(parsing_dict['about_location']).text

    # house_rules
    current_listing['house_rules'] = driver.find_element_by_xpath(parsing_dict['house_rules']).text.replace('\n',' ')

    # map coordinates
    url_string = str(page_source)
    p_lat = re.compile(r'"lat":([-0-9.]+),')
    p_lng = re.compile(r'"lng":([-0-9.]+),')
    try:
        lat = p_lat.findall(url_string)[0]
        lng = p_lng.findall(url_string)[0]
    except:
        lat = lon = -999
    current_listing['coordindates'] = (lat,lng)

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
                print(f'{date}-{availability}')
                calendar[f'month_{str(current_month)}_day_{date}'] = availability

        # next_month
        for dd in oto[2].find_all('td'):
            if len(dd.text)!=0:
                date = dd.text 
                try :
                    availability = dd.find('div')['data-is-day-blocked']
                except :
                    availability = 'Na'
                print(f'{date}-{availability}')
                calendar[f'month_{str(current_month+1)}_day_{date}'] = availability

        bookings = pd.Series(calendar)
        current_listing['bookings'] = bookings
        current_listing['availability_rate'] = (bookings[bookings=='true'].shape[0]/bookings.shape[0])
    else:
        current_listing['bookings'] = None
        current_listing['availability_rate'] = None
        
driver.quit()

