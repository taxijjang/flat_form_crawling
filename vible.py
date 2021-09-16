# 내장 라이브러리
import re
import os
import logging
from urllib import parse
from multiprocessing import Pool
from multiprocessing import Manager
# 외부 라이브러리
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

BASE_URL = 'https://www.vible.co/'

manager = Manager()

total_course_urls = manager.list()
total_video_count = manager.list()


def browser():
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(executable_path='./chromedriver', options=options)
    return driver


def get_celebrity_urls():
    total_celebrity_urls = []
    driver = browser()

    target_url = f'{BASE_URL}ko/categories/'
    driver.get(target_url)

    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'categories')))
    except TimeoutException:
        logging.info("해당 page에 데이터가 없다.")
        driver.close()
        return total_celebrity_urls

    html = driver.page_source
    if html:
        celebrity_urls = set(re.findall(r'ko/categories/\w+', str(html)))
        total_celebrity_urls.extend(celebrity_urls)
    driver.close()
    return total_celebrity_urls


def get_course_urls(celebrity_url) -> None:
    global total_course_urls
    driver = browser()
    target_url = f'{BASE_URL}{celebrity_url}'
    driver.get(target_url)
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'txt_box')))
    except TimeoutException:
        logging.info("해당 page에 데이터가 없다.")
        driver.close()
        return None
    html = driver.page_source
    if html:
        course_path = celebrity_url.replace("categories", "class")
        print(course_path)
        course_paths = set(re.findall(fr'{course_path}/\d+', str(html)))
        course_paths = set(course_path.replace('"', '') for course_path in course_paths)
        print(os.getpid(), len(course_paths))
        total_course_urls.extend(course_paths)
        if target_url != driver.current_url:
            driver.close()
            return total_course_urls
    driver.close()
    return total_course_urls


def get_video_counts(course_url: str) -> None:
    global total_video_count
    driver = browser()
    target_url = BASE_URL + course_url
    driver.get(target_url)

    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'cont_tit')))
    except TimeoutException:
        logging.info("해당 page에 데이터가 없다.")
        driver.close()
        return None

    html = driver.page_source
    try:
        if html:
            video_count_data = ''.join(re.findall(r'All Lessons \d+', str(html)))
            video_count = set(re.findall(r'\d+', video_count_data))
            total_video_count.extend(video_count)
            print(os.getpid(), target_url, video_count)
    except Exception as ex:
        logging.info("해당 클래스에서 강의 정보를 찾지 못하여 비디오 개수 0으로 추가.")
        total_video_count.append(0)
        driver.close()
    driver.close()


def sum_video_count() -> int:
    return sum(map(int, total_video_count))


def main() -> None:
    course_pool = Pool(processes=os.cpu_count() // 2)
    course_pool.map(get_course_urls, get_celebrity_urls())

    course_pool.close()
    course_pool.join()

    video_pool = Pool(processes=os.cpu_count() // 2)
    video_pool.map(get_video_counts, total_course_urls)

    video_pool.close()
    video_pool.join()

    print(f'클래스 갯수: {len(total_course_urls)}, 동영상 갯수: {sum_video_count()}')
    # 클래스 갯수: 19, 동영상 갯수: 332


if __name__ == "__main__":
    main()
