import time
import requests
import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup

# selenium for traversing the site
CHROMEDRIVER = '/home/takis/Desktop/sckool/chromedriver_linux64/chromedriver'
URL = 'https://www.airbnb.com/s/Rethimnon--Greece/homes'

driver = webdriver.Chrome(CHROMEDRIVER)
driver.get(URL)
time.sleep(5) # Let the user actually see something!

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')

driver.quit()

page_source = driver.page_source
soup = BeautifulSoup(page_source, 'lxml')

# beautiful soup used with pregenerated urls

# https://www.airbnb.com/s/Rethimnon--Greece/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&flexible_trip_dates%5B%5D=august&flexible_trip_dates%5B%5D=july&flexible_trip_lengths%5B%5D=weekend_trip&date_picker_type=calendar&place_id=ChIJF1hMghZ1mxQR89x2bdQcDOk&federated_search_session_id=a6171eea-428b-4d2b-a085-347be5322360&search_type=unknown&pagination_search=true&items_offset=20&section_offset=4
# https://www.airbnb.com/s/Rethimnon--Greece/homes?pagination_search=true&items_offset=20
# https://www.airbnb.com/s/Rethimnon--Greece/homes?adults=1&refinement_paths%5B%5D=%2Fhomes&tab_id=home_tab&place_id=ChIJF1hMghZ1mxQR89x2bdQcDOk&flexible_trip_dates%5B%5D=august&flexible_trip_dates%5B%5D=july&flexible_trip_lengths%5B%5D=weekend_trip&date_picker_type=calendar&room_types%5B%5D=Entire%20home%2Fapt&room_types%5B%5D=Private%20room&room_types%5B%5D=Hotel%20room&search_type=filter_change
# https://www.airbnb.com/s/Rethimnon--Greece/homes?pagination_search=true&items_offset=20&room_types%5B%5D=Entire%20home%2Fapt&room_types%5B%5D=Private%20room&room_types%5B%5D=Hotel%20room&search_type=filter_change

pages = []
counter = 0

for i in range(0,500,20):
    
    URL = f'https://www.airbnb.com/s/Rethimnon--Greece/homes?pagination_search=true&items_offset={str(i)}&room_types%5B%5D=Entire%20home%2Fapt&room_types%5B%5D=Private%20room&room_types%5B%5D=Hotel%20room&search_type=filter_change'
    
    try :
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, 'html.parser')
        pages.append(soup)
        print(str(i))
        counter += 1
    except Exception as e:
        print(f'error during : {URL}' )
    
print(f'parsed : {str(counter)} pages')
        
len(pages)

# given a page (soup), parse all of its listings

def parse_airbnb_page(soup):

    listing_items = soup.find_all('div', class_='_8ssblpx')
    listing_dict = {}

    for i,r in enumerate(listing_items,start=1):
        
        # print(f'{25*"-"}{str(i)}{25*"-"}')        
        # instantiate a temp dict object to hold room specs
        temp_room = {}
        
        # get combinded text
        temp_room['combined_text'] = r.text    

        # get text list
        temp_room['list_text'] = [x.text for x in r.find('div', class_='_12oal24')]

        # get urls
        temp_room_key = r.find('a', href=True).get('href')
        temp_room['parsed_url'] = temp_room_key
        temp_room['functional_url'] = f'airbnb.com{temp_room_key}'
        
        # insert temp dict into the general dict
        listing_dict['room'+str(i)] = temp_room

    # dataframe manipulation
    yoki = pd.DataFrame().from_dict(listing_dict,orient='index')
    # yoki.list_text.apply(len)

    list_columns = ['title','badge','capacity','amenities','reviews']
    # pd.DataFrame(yoki["list_text"].to_list(), columns=list_columns)

    soki = yoki.list_text.apply(pd.Series)
    soki.columns = list_columns

    moki = yoki.merge(soki,left_index=True, right_index=True)
    return moki

df_list = [parse_airbnb_page(page) for page in pages]
df = pd.concat(df_list).reset_index(drop=True)

df.functional_url.tail(1).squeeze()
df.functional_url.nunique()
df.shape