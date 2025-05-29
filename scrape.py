import sys
import os
import glob
import re
import time
import urllib.request
from bs4 import BeautifulSoup
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = webdriver.ChromeOptions()
options.add_argument("--headless=new")

filename = sys.argv[1]
path = sys.argv[2]

with open(filename) as fp:
  soup = BeautifulSoup(fp)

  body = soup.find("div", role="main")

  # print(body)

  containers = body.find_all("div", class_="_3-95")

  captured = {}

  group = ''
  group_dir = ''

  for container in containers:

    title = container.find("div", class_="_a6-i")

    if title:
      if title.contents == ["Collection"]:
        group = title.next_sibling.div.div.contents[0]

        print()
        print(f'--- {group} ---')

        captured[group] = []

        group_dir = os.path.join(os.path.join(path), group)

        if not os.path.exists(group_dir):
          try:
            os.mkdir(group_dir)
          except FileExistsError:
            ""

    else:
      if container.div:
        username = container.div.div.a.text

        download_url = container.div.div.a["href"]

        post_id = download_url.split('/')[-2]

        # next = True

        srcs = []

        # check if this post has already been downloaded.
        matches = glob.glob(os.path.join(group_dir, f'{username}___{post_id}___*.jpg'))
        if matches and len(matches) > 0:
          print(f'Skipping {username} {download_url}')
          continue

        driver = webdriver.Chrome(options=options)
        driver.get(download_url)
        # driver.page_source

        try:
          ignored_exceptions=(selenium.common.exceptions.NoSuchElementException,selenium.common.exceptions.StaleElementReferenceException,)
          page_container = WebDriverWait(driver, 2, ignored_exceptions=ignored_exceptions).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "x1yvgwvq"))
          )

        except selenium.common.exceptions.TimeoutException:
          print('FAIL',username, download_url)
          pass
          continue

        try:
          closer = driver.find_element(By.CSS_SELECTOR, '[aria-label="Close"]')
          closer.click()

        except selenium.common.exceptions.NoSuchElementException:
          pass

        except selenium.common.exceptions.ElementNotInteractableException:
          pass

        except selenium.common.exceptions.StaleElementReferenceException:
          pass

        multi = False
        try:
          next = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Next"]')
          if(next):
            multi = True

        except selenium.common.exceptions.NoSuchElementException:
          pass

        def download_single(driver):
          try:
            img = driver.find_element(By.XPATH, '//div[@class="_aagv"]//img')
            # print('img', img)
            if img and img.get_attribute('src'):
              # print('Single', img.get_attribute('src'))
              return [img.get_attribute('src')]

          except selenium.common.exceptions.NoSuchElementException:
            # print(driver.find_element(By.XPATH, "/html/body").get_attribute('innerHTML'))
            pass

        def download_single_retry(driver):
          count = 0;

          while count < 3:
            try:
              srcs = download_single(driver)
              return srcs

            except selenium.common.exceptions.StaleElementReferenceException:
              count += 1
              time.sleep(2)


        def download_page(driver):
          srcs = []
          imgs = driver.find_elements(By.XPATH, '//li[@class="_acaz"]//img')

          if len(imgs) > 0:
            for img in imgs:
              srcs.append(img.get_attribute('src'))

          return srcs

        def download_page_retry(driver):
          count = 0;

          while count < 3:
            try:
              srcs = download_page(driver)
              return srcs

            except selenium.common.exceptions.StaleElementReferenceException:
              count += 1
              time.sleep(2)

        def click_next(driver):
          try:
            next = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Next"]')
            next.click()
            return True

          except selenium.common.exceptions.NoSuchElementException:
            pass
            return False

          # There's a weird popup intecepting clicks here and I don't know what to do about it.
          #  <div class="_ap3a _aaco _aacw _aad3 _aad6 _aadc" dir="auto">...</div>
          except selenium.common.exceptions.ElementClickInterceptedException:
            pass
            return False


        def click_next_retry(driver):
          count = 0;

          while count < 3:
            try:
              result = click_next(driver)
              return result

            except selenium.common.exceptions.StaleElementReferenceException:
              count += 1
              time.sleep(2)


        def download_multiple(driver):
          next = True
          srcs = []

          while next:
            results = download_page_retry(driver)
            if results and len(results) > 0:
              srcs += results

              next = click_next_retry(driver)

          # Return only unique results
          if srcs and len(srcs):
            srcs = list(set(srcs))

          return srcs


        if not multi:
          srcs = download_single_retry(driver)

        else:
          srcs = download_multiple(driver)

        if not srcs or len(srcs) == 0:
          print('EMPTY', username, download_url)
          continue

        print('DOWNLOADING', username)
        i = 0
        for src in srcs:
          filename = os.path.join(group_dir, f'{username}___{post_id}___{i}.jpg')
          print(src, filename)
          urllib.request.urlretrieve(src, filename)
          i += 1

        # exit()

  driver.quit()
