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


NUM_CORES = multiprocessing.cpu_count()
SCROLL_PAUSE_SEC = 1

driver = webdriver.Chrome(executable_path='./chromedriver')
driver.implicitly_wait(5)
manager = Manager()


def main():
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

    base_url = 'https://class101.net'

    class_url_list = get_class_url_list(base_url, category_dict)
    print(class_url_list)
    video_count = get_video_count_in_product(base_url, class_url_list)
    return video_count


def get_class101_class_dict():
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


def get_class_url_list(base_url, category_path_dict) -> List:
    class_url_list = []
    for category_name, category_path in category_path_dict.items():
        page = 1
        while True:
            target_url = base_url + f'/search?category={category_path}&page={page}&sort=recommendOrder&state=sales'
            driver.get(target_url)
            try:
                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'infinite-scroll-component')))
            except TimeoutException:
                break
            html = driver.page_source
            if html:
                class_path = set(re.findall(r'/products/\w{20}', str(html)))
                print(os.getpid(), category_path, len(class_path), page)
                class_url_list.extend(class_path)
            page += 1
    print(class_url_list)
    return class_url_list


def get_video_count_in_product(base_url, class_url_list):
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


if __name__ == "__main__":
    # pool = Pool(processes=NUM_CORES)
    # class_path_list = pool.map(get_class_url_list, get_class101_class_dict())
    # print(class_path_list)
    # pool.close()
    # pool.join()
    print(main())