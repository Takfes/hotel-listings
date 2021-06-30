
import time
import requests
import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup


def parse_page(soup):
    
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
    # turn dict into dataframe
    yoki = pd.DataFrame().from_dict(listing_dict,orient='index')
    # split column into multiple columns
    list_columns = ['title','badge','capacity','amenities','reviews']
    soki = yoki.list_text.apply(pd.Series)
    soki.columns = list_columns
    # merge initial with derived above df
    moki = yoki.merge(soki,left_index=True, right_index=True)
    return moki
