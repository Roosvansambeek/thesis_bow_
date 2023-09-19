import requests
from bs4 import BeautifulSoup
# Installing and starting up Chrome using Webdriver Manager
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import csv
import math

chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# make a get request to the course overview page
url = 'https://uvt.osiris-student.nl/#/onderwijscatalogus/extern/cursussen'
driver.get(url)

time.sleep(5)

osi_language = driver.find_elements(By.CLASS_NAME, 'osi-language')[0]
actions = ActionChains(driver)
actions.move_to_element(osi_language).click().perform()

time.sleep(5)

# Check how many courses are on this course list page
courses = driver.find_elements(By.TAG_NAME, 'osi-course-item')
courses_per_page = len(courses)

i = 0
while i < courses_per_page:
    # re-find the course element to prevent stale element reference error
    course = driver.find_elements(By.TAG_NAME, 'osi-course-item')[i]
        
    # Click on course page
    actions = ActionChains(driver)
    actions.move_to_element(course).click().perform()
    print(f'opened course nummer {i + 1}')
        
    time.sleep(5)

    # Get the HTML source code of the last page
    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    
    course_name = soup.find('span', class_='font-heading-1 osi-white text text-md').get_text().strip()
    course_name_parts = course_name.split("\n")
    course_name = course_name_parts[0].strip()
    course_code = course_name_parts[1].strip()
    language = soup.find_all('osi-body')[0].get_text().strip()
    aims = soup.find_all('osi-body')[2].get_text().strip()
    content = soup.find_all('osi-body')[3].get_text().strip()

    course_dict = {'Course name': course_name, 
                    'Course code': course_code,
                    'Language': language,
                    'Aims': aims,
                    'Content': content}
        
    with open('courses.csv', 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=course_dict.keys())
        if csvfile.tell() == 0:  # Check if the file is empty
            writer.writeheader()  # Write the header row
        writer.writerow(course_dict)
                
    print(f'Succesfully scraped course number {i + 1}, {course_name}')
        
    time.sleep(5)
        
    # Close course page
    close = driver.find_element(By.CLASS_NAME, "bar-button-clear")
    actions = ActionChains(driver)
    actions.move_to_element(close).click().perform()
        
    time.sleep(5)

    # Check how many courses are on this course list page
    courses = driver.find_elements(By.TAG_NAME, 'osi-course-item')
    courses_per_page = len(courses)
    i += 1
