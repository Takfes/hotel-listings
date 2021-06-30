import time
import requests
import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup

# selenium for traversing the site
CHROMEDRIVER = '/home/takis/Desktop/sckool/chromedriver_linux64/chromedriver'
URL = 'https://www.airbnb.com/s/Rethimnon--Greece/homes'

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')

driver = webdriver.Chrome(CHROMEDRIVER)
driver.get(URL)
time.sleep(5) # Let the user actually see something!

page_source = driver.page_source
soup = BeautifulSoup(page_source, 'lxml')
driver.quit()