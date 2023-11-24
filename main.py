from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from Keywords import main_keywords, keywords2
import time
import os
import csv
import re


class Youtube_ChannelScraping():
    def __init__(self, driver):
        self.DRIVER = driver
        self.XPATHS()
    
    def XPATHS(self):
        self.URL_TEMPLATE    =  "https://www.youtube.com/results?search_query=USA+{}&sp=CAM%253D"
        self.CHANNEL_LINK    =   "//ytd-video-renderer//ytd-channel-name//a"
        self.SUBSCRIBERS     =   "//yt-formatted-string[@id='subscriber-count']"
        self.ABOUT_TAB       =    "//yt-tab-shape[@tab-title='About']"
        self.LOCATION        =   "//*[@id='details-container']/table/tbody/tr[2]/td[2]"
        
    
    def ScrapLinks(self, keyword):
        keyword = keyword.replace(' ', '+')
        self.URL = self.URL_TEMPLATE.format(keyword)
        
        self.DRIVER.get(self.URL)
        WebDriverWait(driver, timeout=20).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@id='content']")))
        Results = self.DRIVER.find_elements(By.XPATH, self.CHANNEL_LINK)
        
        for i in range(1, 10000):
            try:
                driver.find_element(By.XPATH, "//ytd-message-renderer//yt-formatted-string[text()='No more results']")
                past_links = [link.replace('\n', '') for link in self.ReadLinks()]
                [self.SaveLinks(x.get_attribute('href')) for x in Results if x.get_attribute('href') not in past_links]
                break
            except: pass
            
            driver.execute_script("arguments[0].scrollIntoView(true);", Results[len(Results)-1])
            Results = self.DRIVER.find_elements(By.XPATH, self.CHANNEL_LINK)
            time.sleep(2)
            
    def ScrapData(self):
        Links = self.ReadLinks()
        
        for link in Links:
            self.DRIVER.get(link)
            time.sleep(3)
            
            subscriber = self.DRIVER.find_element(By.XPATH, self.SUBSCRIBERS).text
            subscribers = "".join(re.findall(r"([\d.]*[KM]*)", subscriber))
            
            WebDriverWait(self.DRIVER, timeout=20).until(EC.element_to_be_clickable((By.XPATH, self.ABOUT_TAB)))
            WebDriverWait(self.DRIVER, timeout=20).until(EC.presence_of_all_elements_located((By.XPATH, self.ABOUT_TAB)))
            self.DRIVER.find_element(By.XPATH, self.ABOUT_TAB).click()
            
            try:
                WebDriverWait(self.DRIVER, timeout=20).until(EC.presence_of_all_elements_located((By.XPATH, self.LOCATION)))
                location = self.DRIVER.find_element(By.XPATH, self.LOCATION).text
            except: location = "USA"
            
            if subscribers != "" and location != "India" and location != "Pakistan":
                if "K" in subscribers and float(subscribers.replace('K',''))*1000 > 50000: 
                    id = "".join(re.findall(r"/(@[\w ]+)", link))
                    try:
                        links = self.DRIVER.find_elements(By.XPATH, '//*[@id="link-list-container"]//a')
                        links = [x.text for x in links]
                        links = " ".join(links.text)
                    except: links:None
                    self.save_to_csv("data/KChannels.csv", [id, links, subscribers])
                    
                elif "M" in subscribers:
                    id = "".join(re.findall(r"/(@[\w ]+)", link))
                    try:
                        links = self.DRIVER.find_elements(By.XPATH, '//*[@id="link-list-container"]//a')
                        links = [x.text for x in links]
                        links = " ".join(links.text)
                    except: links:None
                    self.save_to_csv("data/MChannels.csv", [id, links, subscribers])
    
    def save_to_csv(self, filename, data):
        file_exists = os.path.isfile(filename)
        with open(filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["ChannelID", "Links", "Subscribers"])

            writer.writerow(data)
    
    def SaveLinks(self, link):
        with open("data/Links.txt", "a") as file:
            file.write(link + "\n")
    
    def ReadLinks(self):
        with open("Links.txt", "r") as file:
            links = file.readlines()
            return links
        


driver = webdriver.Chrome()
obj = Youtube_ChannelScraping(driver)

try:
    obj.ScrapData()
except: 
    time.sleep(2)
    pass

# for keyword in keywords2:
#     try:
#         print(keyword)
#         obj.ScrapLinks(keyword)
#     except: pass

