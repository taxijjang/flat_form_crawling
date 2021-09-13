# 내장 라이브러리
import re
import os
import multiprocessing
from typing import *
from multiprocessing import Pool
from multiprocessing import Manager
# 외부 라이브러리
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

manager = Manager()
total_class_urls = manager.list()


def browser():
    driver = webdriver.Chrome(executable_path='./chromedriver')
    return driver


def append_class_url(class_url):
    total_class_urls.append(class_url)


def get_class_urls():
    base_url = 'https://class101.net'
    category_dict = dict(
        드로잉='604f1c9756c3676f1ed00304',
        공예='604f1c9756c3676f1ed00317',
        요리음료='604f1c9756c3676f1ed0034f',
        베이킹디저트='604f1c9756c3676f1ed0035e',
        음악='604f1c9756c3676f1ed00365',
        운동='604f1c9756c3676f1ed00373',
        라이프='604f1c9756c3676f1ed0037e',
        사진영상='604f1c9756c3676f1ed00389',
        수익창출='604f1c9756c3676f1ed003b2',
        디자인='604f1c9756c3676f1ed0038e',
        개발='604f1c9756c3676f1ed00397',
        직무교육='604f1c9756c3676f1ed003a2',
        글쓰기='604f1c9756c3676f1ed003c4',
        언어='604f1c9756c3676f1ed003cd',
        아동교육='604f1c9756c3676f1ed003d6',
        DIY키트='605b0d1be0b389a99bf69fce',
    )

    return list(category_dict.values())


def get_class_url_list(class_url) -> List:
    global total_class_urls
    base_url = 'https://class101.net'
    driver = browser()
    page = 1
    while True:
        target_url = base_url + f'/search?category={class_url}&page={page}&sort=recommendOrder&state=sales'
        driver.get(target_url)
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'infinite-scroll-component')))
        except TimeoutException:
            driver.close()
            break
        html = driver.page_source
        if html:
            class_path = set(re.findall(r'/products/\w{20}', str(html)))
            print(os.getpid(), class_url, len(class_path), page)
            total_class_urls.extend(class_path)
        page += 1


def get_video_count_in_product(base_url, class_url_list):
    driver = browser()
    total_video_count = 0
    for class_url in class_url_list:
        target_url = base_url + class_url
        driver.get(target_url)

        html = driver.page_source
        try:
            if html:
                print(target_url)
                video_count_data = ''.join(re.findall(r'\d+개 세부강의', str(html)))
                video_count = int(re.findall(r'\d+', video_count_data).pop())
                total_video_count += video_count
                print(video_count)
        except Exception:
            print("ASDF")
    return total_video_count

def test_func(link):
    driver = browser()
    driver.get('https://class101.net')
    print(os.getpid())

if __name__ == "__main__":
    pool = Pool(processes=6)
    # for class_url in get_class_urls():
    #     pool.apply_async(get_class_url_list, args=(class_url,), callback=append_class_url)
    pool.map(get_class_url_list, get_class_urls())
    # class_urls = get_class_urls()
    # for i in range(0, len(get_class_urls())):
    #     pool.apply_async(test_func, args={class_urls[i]})

    pool.close()
    pool.join()
    print(total_class_urls)
