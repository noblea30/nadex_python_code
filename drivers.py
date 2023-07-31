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
        return get_time()
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
  element = WebDriverWait(driver,5*60).until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "5 MINUTE")))
  element.click()
  time.sleep(4) 
  print("it's open")
  
def check_prices():
  #get the high, low, ind, name, etc of each stock
  #return all values along with the time.
  pass
  t = get_time()
  #print("checking now")
  stocks = driver.find_elements(By.CLASS_NAME, "market-list_group")
  if len(stocks)<2:#must be at midnight turned off for now
    keep_awake()
    time.sleep(120)
    return check_prices()
  data = {}
  data[t] = {}
  try:
      for i in range(2):  #only do 2 stocks for now.  range(len(stocks)):
        s = stocks[i]
        text = s.text
      #for s in stocks:
        #print(s.text)
        s.click()
        keep_awake_fast()
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
          keep_awake_fast()
          WebDriverWait(driver, 3).until_not(EC.presence_of_element_located((By.CLASS_NAME, "market-list_content")))
        except:
          s.click()
          WebDriverWait(driver, 3).until_not(EC.presence_of_element_located((By.CLASS_NAME, "market-list_content")))
        #time.sleep(3)
        stocks = driver.find_elements(By.CLASS_NAME, "market-list_group")
        
      return data
  except:
        keep_wake()
        time.sleep(60)
        return check_prices


def get_second_level_price(buy, name, tick):
    #opens the ticket, gets last minute price and waits.
     #click stock name
    tick_ind = -1*tick+3 
     
    index = -100
    if buy == -1:
        index = 1  #get the index 2 instead of -1 to click on the element
    elif buy ==1:
        index = 2
    else:
        print("error, why am I buying this? ", buy, name, tick)
        while 1:
            pass
    stocks = driver.find_elements(By.CLASS_NAME, "market-list_group")
    for s in stocks:
        if name in s.text:
            s.click()
        else:
            #print("." + s.text + ".")
            pass
    
    #click ticket (buy or sell)
        content = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "market-list_content")))
        #print(len(content.text))
        if len(content.text) < 40:
            time.sleep(.1)
            content = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "market-list_content")))
        ticks =content.find_elements(By.CLASS_NAME, "market-list_item")
        #e = content.find_element(By.XPATH, f"./content[{tick+3}]/element[2][1]")
        e = content.find_element(By.XPATH, f"./dd[{tick_ind}]/div[2]/a[{index}]")
        #/html/body/div[1]/div[3]/div[1]/div/div[2]/div[1]/section[2]/div/div[2]/div/div[1]/div[2]/div/dd[3]/div[2]/a[1]
        #/html/body/div[1]/div[3]/div[1]/div/div[2]/div[1]/section[2]/div/div[2]/div/div[1]/div[2]/div
        #print(e.text)
        ret = e.text
        e.click()
        
        
        try:
            button_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button.btn.btn--primary.enabled[type="submit"]')))
            button_element.click()
        except:
            print("never found it")
            return -1
        time.sleep(2)
        #print("closing stuff now")
        stocks = driver.find_elements(By.CLASS_NAME, "market-list_heading")
        #s = driver.find_elements(By.CLASS_NAME, "market-list_heading")[i]
        for s in stocks:
            if name in s.text:
                s.click() #close the ticks
        e = driver.find_element(By.CLASS_NAME, "ticket_toggle-visibility")
        e.click()  #tear off ticket
        
        return(ret)
    #find value

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

    pyautogui.moveTo((curr[0] + 5*direction,curr[1]+5*direction))
    curr = pyautogui.position()
    pyautogui.press('shift')
    steps -=1
    if steps ==0:
        steps = 50
        direction *= -1
    
