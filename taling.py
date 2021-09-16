# 내장 라이브러리
import json
import re
import os
import logging
from typing import *
from multiprocessing import Pool
from multiprocessing import Manager
# 외부 라이브러리
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

manager = Manager()
total_course_urls = manager.list()
total_video_count = manager.list()

BASE_URL = 'https://taling.me/vod/'


def browser():
    driver = webdriver.Chrome(executable_path='./chromedriver')
    return driver


def get_course_urls():
    total_course_urls = []
    base_api_url = 'https://taling.me/api3/vod/vodListDetail.php?'
    categories = dict(
        커리어=2,
        뷰티_헬스=3,
        디자인_영상=4,
        외국어=5,
        라이프=7,
        머니=11,
        취미_공예=22,
    )

    for category_name, category_id in categories.items():
        page = 1
        while True:
            target_url = f'{base_api_url}page={page}&cateMain={category_id}'
            req = requests.get(target_url)
            response_data = json.loads(req.text)

            data = response_data.get('data')
            if not data:
                break

            courses = data.get('list')
            page += 1

            for course in courses:
                total_course_urls.append(f'{BASE_URL}view/{course.get("id")}')
    return total_course_urls


def get_video_counts(class_url: str) -> None:
    global total_video_count
    driver = browser()
    driver.get(class_url)

    html = driver.page_source
    print(html)
    try:
        if html:
            video_count_data = ''.join(re.findall(r'\d+강<', str(html)))
            video_count = re.findall(r'\d+', video_count_data)
            total_video_count.extend(video_count)
            print(os.getpid(), class_url, video_count)
    except Exception as ex:
        logging.info("해당 클래스에서 강의 정보를 찾지 못하여 비디오 개수 0으로 추가.")
        total_video_count.append(0)
    driver.close()


def sum_video_count() -> int:
    return sum(map(int, total_video_count))


def main() -> None:
    video_pool = Pool(processes=os.cpu_count() // 2)
    video_pool.map(get_video_counts, get_course_urls())

    video_pool.close()
    video_pool.join()

    print(f'클래스 갯수: {len(get_course_urls())}, 동영상 갯수: {sum_video_count()}')


if __name__ == "__main__":
    main()
