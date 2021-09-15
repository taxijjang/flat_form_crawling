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

BASE_URL = 'https://www.inflearn.com/'
manager = Manager()

total_video_count = manager.list()


def browser():
    options = webdriver.ChromeOptions()
    # options.add_argument(
    #     "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36")
    driver = webdriver.Chrome(executable_path='./chromedriver', options=options)
    return driver


def get_course_urls() -> None:
    total_course_urls = []
    driver = browser()
    page = 1
    while True:
        target_url = f'{BASE_URL}courses?order=seq&page={page}'
        driver.get(target_url)
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'courses_container')))
        except TimeoutException:
            logging.info("해당 page에 데이터가 없다.")
            driver.close()
            return total_course_urls
        html = parse.unquote(driver.page_source)
        if html:
            course_paths = set(re.findall(r'course/[ㄱ-ㅣ가-힣a-zA-Z-]+"', str(html)))
            course_paths = set(course_path.replace('"', '') for course_path in course_paths)
            print(os.getpid(), len(course_paths), page)
            total_course_urls.extend(course_paths)
            if target_url != driver.current_url:
                return total_course_urls
        page += 1
    return total_course_urls


def get_video_counts(class_url: str) -> None:
    global total_video_count
    driver = browser()
    target_url = BASE_URL + class_url
    driver.get(target_url)

    html = parse.unquote(driver.page_source)
    convert_html = ''.join(str(html).split())
    try:
        if html:
            video_count_data = ''.join(re.findall(r'총\d+개수업', convert_html))
            video_count = set(re.findall(r'\d+', video_count_data))
            total_video_count.extend(video_count)
            print(os.getpid(), target_url, video_count)
    except Exception as ex:
        logging.info("해당 클래스에서 강의 정보를 찾지 못하여 비디오 개수 0으로 추가.")
        total_video_count.append(0)
    driver.close()


def sum_video_count() -> int:
    return sum(map(int, total_video_count))


def main() -> None:
    total_course_urls = get_course_urls()

    # video_pool = Pool(processes=os.cpu_count() // 2)
    video_pool = Pool(processes=2)
    video_pool.map(get_video_counts, total_course_urls)

    video_pool.close()
    video_pool.join()

    print(f'클래스 갯수: {len(total_course_urls)}, 동영상 갯수: {sum_video_count()}')
    # 클래스 갯수: 1155, 동영상 갯수: 40318


if __name__ == "__main__":
    main()
