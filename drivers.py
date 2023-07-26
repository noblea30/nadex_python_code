from calculations import *
from data_storage import *
from unique_info import *
from info import *
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pyautogui
#from data_storage import *
#from selenium import webdriver
#from selenium.webdriver.common.by import By
#from selenium.webdriver.support.ui import WebDriverWait
#from selenium.webdriver.support import expected_conditions as EC
#from time import sleep
from selenium.webdriver.common.keys import Keys
#from selenium.common import exceptions
#from selenium.webdriver.common.by import By
#import time
#import csv
#from advanced_selenium_options import Chrome, By
driver = None

def open_browser(url,profile, path, headless=False):
  global driver
  options = uc.ChromeOptions()
  #profile = "C:/Users/Public/Public Documents/Chrome_details/Default"
  #path = "C:/Users/Public/Public Documents/Chrome_details/chromedriver.exe"
  options.user_data_dir = profile
  driver = uc.Chrome(use_subprocess=True, options=options, headless = headless)
  print(url)
  driver.get(url)
  print("got it now.")

def open_browser_1(url, profile, path, headless=False):
    global driver
    #uc.TARGET_VERSION=109
    driver = uc.Chrome(use_subprocess=True,version_main=108)
    driver.get(url)
def get_time():
  try:
        e = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CLASS_NAME, "account_time-value")))
  except:
        print("oops, it's not there")
        while 1:
            pass
  #print("in file", convert_time_to_epoch(e.text))
  #print(e.text)

  return convert_time_to_epoch(e.text)



def login_real():
  cl = "login_submit"
 
  try:
    e = driver.find_element(By.CLASS_NAME, cl)
  except:
    return
  e.click()
  wait = WebDriverWait(driver, 100)
  wait.until(EC.number_of_windows_to_be(2))
  print("found second window")
  main_window_handle = driver.current_window_handle
  for handle in driver.window_handles:
    if handle != main_window_handle:
        driver.switch_to.window(handle)
        print("switched to second window")
        break
  time.sleep(5)
  un = driver.find_element(By.ID, "username")
  un.send_keys('andyrew1008')
  pw = driver.find_element(By.ID, "password")
  pw.send_keys("Ha52ss!!")
  pw.send_keys(Keys.ENTER)
  print("should be good now")



def open_stocks():
  #just opens the 5 minute forex to allow gathering data.
  pass
  #click 5 minute (that's all I guess.)
  element = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "5 MINUTE")))
  element.click()
  time.sleep(4) 
  print("it's open")
  
def check_prices():
  #get the high, low, ind, name, etc of each stock
  #return all values along with the time.
  pass
  t = get_time()
  print("checking now")
  stocks = driver.find_elements(By.CLASS_NAME, "market-list_group")
  data = {}
  data[t] = {}
  for i in range(2):  #only do 2 stocks for now.range(len(stocks)):
    s = stocks[i]
    text = s.text
  #for s in stocks:
    print(s.text)
    s.click()
    content = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "market-list_content")))
    #print(len(content.text))
    if len(content.text) < 40:
      time.sleep(.1)
      content = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "market-list_content")))
    data[t]= parse_data(content.text,text,data[t])
    #print("I found it.  It is: ")
    #print(t)
    #print("now it's done")
    #time.sleep(3)
    s = driver.find_elements(By.CLASS_NAME, "market-list_heading")[i]
    #s = stocks[i]
    s.click()
    try:
      WebDriverWait(driver, 3).until_not(EC.presence_of_element_located((By.CLASS_NAME, "market-list_content")))
    except:
      s.click()
      WebDriverWait(driver, 3).until_not(EC.presence_of_element_located((By.CLASS_NAME, "market-list_content")))
    #time.sleep(3)
    stocks = driver.find_elements(By.CLASS_NAME, "market-list_group")
    
  return data




direction  = 1
mouse_location =  pyautogui.position()
steps = 50
curr = pyautogui.position()
def keep_awake():
    #return
    global direction
    global mouse_location
    curr = pyautogui.position()
    if mouse_location != curr:  #I must have moved it.  dont' do anything
        mouse_location = curr
        return
    #prev = curr
    for i in range(0,50):
        pyautogui.moveTo((curr[0],curr[1]+direction*i*5))
        curr = pyautogui.position()
        time.sleep(.1)
        if pyautogui.position() != curr:
            return
    direction *= -1
    for i in range(0,3):
        pyautogui.press('shift')
    mouse_location = curr

def keep_awake_fast():  #can call this funtion and it won't take much time.  Need to call it often though.
    global direction
    global mouse_location
    global steps
    global curr
    curr = pyautogui.position()
    if mouse_location !=curr:
        mouse_location = curr
        return

    pyautogui.moveTo((curr[0],curr[1]+5*direction))
    curr = pyautogui.position()
    steps -=1
    if steps ==0:
        steps = 50
        direction *= -1
    
