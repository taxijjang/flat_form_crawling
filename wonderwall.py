# 내장 라이브러리
import re
import os
import json
import logging
from typing import *
from multiprocessing import Pool
from multiprocessing import Manager
# 외부 라이브러리
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

manager = Manager()
total_course_urls = manager.list()
total_video_count = manager.list()

BASE_URL = 'https://wonderwall.kr/'


def browser():
    driver = webdriver.Chrome(executable_path='./chromedriver')
    return driver


def get_course_urls():
    target_url = 'https://api.wonderwall.kr/v2/sectors'
    response_data = json.loads(requests.get(target_url).text)
    data = response_data.get('data')

    course_urls = []
    for sector in data:
        course_urls.extend(set(sector.get('classList')))
    return course_urls


def get_video_counts(course_url: str) -> None:
    global total_video_count
    target_url = f'{BASE_URL}class/{course_url}'
    driver = browser()
    driver.get(target_url)

    html = driver.page_source
    try:
        if html:
            video_play_times = re.findall(r'\d{2}:\d{2}', str(html))
            total_video_count.extend(video_play_times)
            print(os.getpid(), course_url, len(video_play_times))
    except Exception as ex:
        logging.info("해당 클래스에서 강의 정보를 찾지 못하여 비디오 개수 0으로 추가.")
        total_video_count.append(0)
    driver.close()


def sum_video_count() -> int:
    return len(total_video_count)


def main() -> None:
    get_course_urls()

    video_pool = Pool(processes=os.cpu_count() // 2)
    video_pool.map(get_video_counts, get_course_urls())

    video_pool.close()
    video_pool.join()

    print(f'클래스 갯수: {len(get_course_urls())}, 동영상 갯수: {sum_video_count()}')
    # 클래스 갯수: 81, 동영상 갯수: 635

if __name__ == "__main__":
    main()
