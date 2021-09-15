# 내장 라이브러리
import json
# 외부 라이브러리
import requests

BASE_URL = 'https://api2.enfit.net/api/v3/class_search/'


def get_course_and_video_count():
    total_course_count, total_video_count = 0, 0

    headers = {
        # jwt token
        'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.'
                         'eyJpc3MiOiJodHRwczovL3d3dy5jbGFzc3UuY28ua3Iv'
                         'Y2xhc3Mvc2VhcmNoIiwiaWF0IjoxNjMxNjczMjYyLCJl'
                         'eHAiOjE2MzI4ODI4NjIsIm5iZiI6MTYzMTY3MzI2Miwi'
                         'anRpIjoibm56SGx6RVFuT1dTVkROSyIsInN1YiI6MTEw'
                         'MTYsInBydiI6Ijk2MmExNGQ0OGM0MjllM2E2YWFiMzYx'
                         'MGMwMzUyYmZiYjQ1ZWZjNTgifQ.9poC61l7AwsI5qyTF'
                         'ZmKjwJU47kiAeRz1rpuaFkQP7U'
    }

    page = 1
    while True:
        target_url = f"{BASE_URL}{page}"
        req = requests.post(target_url, headers=headers)
        response_data = json.loads(req.text)
        results = response_data.get('results')
        total_page = int(results.get('total_page'))
        if total_page < page:
            return total_course_count, total_video_count

        courses = results.get('list')
        total_course_count += len(courses)

        for course in courses:
            total_video_count += course.get('curriculum_cnt')

        print(page, total_course_count, total_video_count)
        page += 1


def main():
    course_count, video_count = get_course_and_video_count()
    print(f"클래스 갯수: {course_count}, 동영상 갯수: {video_count}")


if __name__ == "__main__":
    main()
    # print(f'클래스 갯수: {len(total_class_urls)}, 동영상 갯수: {sum_video_count()}')
