#!/usr/bin/env python3

# Imports
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException,TimeoutException,ElementNotInteractableException
# Variables
# Getting set number + logins ( stdin )
# email = str(input('Email: '))
# password = str(input('Password: '))
# set_name = str(input('Quizlet Set Name: '))
email = ''
password = ''
set_name = ''
fill = ''
SCROLL_PAUSE_TIME = 0.3

link = 'https://quizlet.com/login'

# Initalizing Driver
driver = webdriver.Firefox()
driver.get(link)
wait = WebDriverWait(driver, 10)

# Logging in
login_element = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[@class="UIButton UIButton--social UIButton--fill UIButton--hero"]')))
login_href = login_element.get_attribute('href')
driver.get(login_href)

email_input = wait.until(EC.visibility_of_element_located((By.XPATH, '//input[@type="email"]')))
email_input.send_keys(email)
email_input.send_keys(Keys.ENTER)

password_input = wait.until(EC.visibility_of_element_located((By.XPATH, '//input[@type="password"]')))
password_input.send_keys(password)
password_input.send_keys(Keys.ENTER)

# Load all sets

all_element = wait.until(EC.visibility_of_element_located((By.XPATH,'//div[@class = "UIDiv RecentFeed-seeMoreLink"]/a')))
all_href = all_element.get_attribute('href')
driver.get(all_href)

# Get scroll height
last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    # Scroll down to bottom
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Wait to load page
    sleep(SCROLL_PAUSE_TIME)

    # Calculate new scroll height and compare with last scroll height
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# Find set to complete
sleep(1)
set_href_element = driver.find_element_by_xpath('//header[@aria-label= "%s" ]/a' % set_name)
set_href = set_href_element.get_attribute('href')

driver.get(set_href)

# Exit Ads
try:
    sleep(1)
    exit_button_element = driver.find_elements_by_xpath('//button[@class = "UILink UILink--revert"]')
    exit_button_element = exit_button_element[-1]
    exit_button_element.click()
except IndexError as e:
    print(e)
    pass


# Finish Write
def write():
    write_href_element = driver.find_element_by_xpath('//a[@aria-label = "Write"]')
    write_href = write_href_element.get_attribute('href')
    driver.get(write_href)

    sleep(2)
    write_progress = int(driver.find_element_by_xpath('//div[@class = "WriteProgress-value"]').text)
    for i in range(write_progress):
        write_textarea_element = wait.until(EC.element_to_be_clickable((By.XPATH,'//textarea[@class = "AutoExpandTextarea-textarea"]')))
        write_textarea_element.send_keys(fill)
        write_textarea_element.send_keys(Keys.ENTER)

        override_write_element = wait.until(EC.element_to_be_clickable((By.XPATH, '//span[@class = "WrittenFeedbackItem-answerOverride"]/button[@class = "UILink"]')))
        override_write_element.click()

    # Go back after finished with write
    driver.get(set_href)
    sleep(1)
    exit_button_element = driver.find_elements_by_xpath('//button[@class = "UILink UILink--revert"]')
    exit_button_element = exit_button_element[-1]
    exit_button_element.click()

sleep(1)
descriptions = driver.find_elements_by_xpath('//span[@class = "SetPageModeButton-description"]')
for description in descriptions:
    if 'Write' in description.text:
        try:
            if description.find_element_by_xpath('.//span[@class = "SetPageModeButton-progress"]').text == 'Finished!':
                print(description.find_element_by_xpath('.//span[@class = "SetPageModeButton-progress"]').text)
                pass
            else:
                print('Doing Write')
                write()
                break
        except NoSuchElementException:
            print('No progress founds, starting write')
            write()
            break

# Finish Spell
def spell():
    terms = {}

    # Change terms to original
    sleep(2)
    original_terms = driver.find_element_by_xpath('//select[@class = "UIDropdown-select"]')
    original_terms.click()
    original_terms_select = original_terms.find_element_by_xpath('//option[@value = "original"]').click()
    sleep(3)

    # Get scroll height
    print('Starting Scroll')
    last_height = driver.execute_script("return document.body.scrollHeight")
    print('last: ',last_height)

    while True:
        print('Scrolling')
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        print('new: ',new_height)
        if new_height == last_height:
            break
        last_height = new_heightterms = {}

    for row in driver.find_elements_by_xpath('//div[@class = "SetPageTerm-content"]'):
        value = row.find_element_by_xpath('.//a[@class = "SetPageTerm-wordText"]/span').text
        key = row.find_element_by_xpath('.//a[@class = "SetPageTerm-definitionText"]/span').text
        terms[key] = value

    sleep(1)


    spell_href_element = driver.find_element_by_xpath('//a[@aria-label = "Spell"]')
    spell_href = spell_href_element.get_attribute('href')
    driver.get(spell_href)
    sleep(1)

    while driver.find_element_by_xpath('//div[@class = "SpellControls-progressValue"]').text != "0":
        try:
            sleep(1)
            driver.find_element_by_xpath('//button[@aria-label = "Continue"]').click()
        except NoSuchElementException:
            sleep(1)
            try:
                question = driver.find_element_by_xpath('//div[@class = "UIDiv SpellQuestionView-inputPrompt--plain"]').text
                spell_input = driver.find_element_by_xpath('//textarea[@class = "AutoExpandTextarea-textarea"]')
                spell_input.send_keys(terms.get(question))
                spell_input.send_keys(Keys.ENTER)
            except:
                break

descriptions = driver.find_elements_by_xpath('//span[@class = "SetPageModeButton-description"]')
for description in descriptions:
    if 'Spell' in description.text:
        try:
            if description.find_element_by_xpath('.//span[@class = "SetPageModeButton-progress"]').text == 'Finished!':
                print('Finished')
                break
            else:
                print('Doing Spell')
                spell()
                break
        except NoSuchElementException:
            print('No progress found, starting spell')
            spell()
            break

driver.get(set_href)
print("Done")

# To Do
# Finish All Activies
