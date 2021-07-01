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
adults = 4
counter = 0    
max_offset = 300
offset_step = 20 # dont change

if __name__ == '__main__':

    for i in range(0,max_offset,offset_step):        
        
        # paginated urls
        base = yield_url(months,adults)
        url = base + f'&pagination_search=true&items_offset={str(i)}'
        print(url)
        print()
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
    # save to disk
    df.to_csv('data/listings.csv',index=False)