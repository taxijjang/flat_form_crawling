# 내장 라이브러리
import re
import os
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
total_video_count = manager.list()


def browser():
    driver = webdriver.Chrome(executable_path='./chromedriver')
    return driver


def class_urls() -> List:
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
    )

    return list(category_dict.values())


def get_class_urls(class_url: List) -> None:
    global total_class_urls
    base_url: str = 'https://class101.net'
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


def get_video_counts(class_url: str) -> None:
    global total_video_count
    base_url: str = 'https://class101.net'
    driver = browser()
    target_url = base_url + class_url
    driver.get(target_url)

    html = driver.page_source
    try:
        if html:
            video_count_data = ''.join(re.findall(r'\d+개 세부강의', str(html)))
            video_count = re.findall(r'\d+', video_count_data)
            total_video_count.extend(video_count)
            print(os.getpid(), target_url, video_count)
    except Exception as ex:
        print(ex)
        driver.close()
        total_video_count.append(0)
    driver.close()


@property
def sum_video_count():
    return sum(map(int, total_video_count))


def main():
    class_pool = Pool(processes=os.cpu_count() // 2)
    class_pool.map(get_class_urls, class_urls())

    class_pool.close()
    class_pool.join()

    video_pool = Pool(processes=os.cpu_count() // 2)
    video_pool.map(get_video_counts, total_class_urls)

    video_pool.close()
    video_pool.join()


if __name__ == "__main__":
    main()
    print(total_class_urls, len(sum_video_count))
