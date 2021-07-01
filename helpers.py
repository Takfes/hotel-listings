import re
import time
import requests
import numpy as np
import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup

def yield_url(months,adults):
    # base url
    base = f'https://www.airbnb.com/s/Rethimnon--Greece/homes?adults={adults}'
    # filter for certain room types
    room_types = '''
        &room_types%5B%5D=Entire%20home%2Fapt
        &room_types%5B%5D=Private%20room
        &room_types%5B%5D=Hotel%20room
        &search_type=filter_change
        '''.replace('\n','').replace(" ", "").strip()
    # add flexible dates to get cost estimates
    if isinstance(months,list):
        flexible_dates = ''
        for m in months: 
            flexible_dates = flexible_dates + f'&flexible_trip_dates%5B%5D={m}'
        flexible_dates = flexible_dates + '&date_picker_type=flexible_dates'
    # currency
    currency = '&display_currency=EUR'
    return base+room_types+flexible_dates+currency


def parse_page(soup):
    # regex float numbers
    regex_float = r"[-+]?\d*\.\d+|\d+"
    # instantiate a dict object to hold room specs
    listing_dict = {}
    # grab listing containers
    containers = soup.find_all('div', class_='_8ssblpx')
    # if there are containers
    if containers:
        # loop through containers to extract info
        for i,r in enumerate(containers,start=1):
            # instantiate a temp dict object to hold individual room specs
            temp_room = {}
            # get combinded text
            temp_room['combined_text'] = r.text    
            # get text list
            temp_room['list_text'] = [x.text for x in r.find('div', class_='_12oal24')]
            # get urls
            temp_room_key = r.find('a', href=True).get('href')
            temp_room['parsed_url'] = temp_room_key
            temp_room['functional_url'] = f'airbnb.com{temp_room_key}'
            # header
            temp_room['header'] = r.find('div',class_="_1olmjjs6").text
            # title
            temp_room['title'] = r.find('div',class_="_5kaapu").text
            # subtitle specs
            specs_list = [x.text for x in r.find_all('span',class_="_3hmsj")]
            for spec in specs_list :
                if 'guest' in spec:
                    temp_room['no_guests'] = float(re.findall(regex_float,spec)[0])
                if 'bedroom' in spec:
                    temp_room['no_bedrooms'] = float(re.findall(regex_float,spec)[0])
                if ('bed' in spec) & ('room' not in spec):
                    temp_room['no_beds'] = float(re.findall(regex_float,spec)[0])
                if 'bath' in spec:
                    temp_room['no_baths'] = float(re.findall(regex_float,spec)[0])
            # rating
            rating_raw = r.find('span',class_='_10fy1f8')
            if rating_raw:
                temp_room['rating'] = float(r.find('span',class_='_10fy1f8').text)
            else :
                temp_room['rating'] = 0.0
            # reviews
            reviews_string = r.find('span',class_='_a7a5sx')
            if reviews_string:
                reviews_string = reviews_string.text.replace('(','').replace(')','')
                temp_room['no_reviews'] = [int(word) for word in reviews_string.split() if word.isdigit()][0]
            else : 
                temp_room['no_reviews'] = 0.0
            # price per night
            price_string = r.find("span", class_="_155sga30")
            if price_string:
                price_string = price_string.text
                temp_room['price'] = int(re.findall(regex_float,price_string)[0])
            else : 
                temp_room['price'] = 0.0
            # insert temp dict into the general dict
            listing_dict['room'+str(i)] = temp_room

    # dataframe manipulation
    # turn dict into dataframe
    if listing_dict:
        yoki = pd.DataFrame().from_dict(listing_dict,orient='index')
        # split column into multiple columns
        list_columns = ['headline','badge','capacity','amenities','dates','reviews_price']
        soki = yoki.list_text.apply(pd.Series)
        soki.columns = list_columns
        # merge initial with derived above df
        moki = yoki.merge(soki,left_index=True, right_index=True)
        return moki