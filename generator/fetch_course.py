import requests
from generator.get_courses import get_courses
from generator.get_points import get_points_for_course
from progress.bar import ChargingBar


def fetch_courses(courses_html: str)-> dict:
    """

    :param courses_html:
    :return: {
        1: [
            {
            'kurskod': 'TATA65',
            'kursnamn': 'Diskret matematik',
            'hp': '6*',
            'termin': 'Termin 1 HT 2025',
            'period': '0', 'link':
            '/kurs/TATA65/ht-2025',
            'hp_uppdelning': [
                {
                'Kod': 'UPG1',
                'Benämning': 'Inlämningsuppgifter',
                'Omfattning': '2'
                },
            ]
            }
        ]
        }
    """

    years = get_courses(courses_html)

    total = 0

    for year in years:
        total += len(years[year])

    print("starting process")

    bar = ChargingBar('Processing', max=total)

    for year in years:
        for index, course in enumerate(years[year]):
            course_link = course["link"]
            response = requests.get(f"https://studieinfo.liu.se/{course_link}")
            points_dict = get_points_for_course(response.content)
            years[year][index]["hp_uppdelning"] = points_dict

            bar.next()

    bar.finish()

    return years



if __name__ == "__main__":
    request = requests.get("https://studieinfo.liu.se/program/6CDDD#curriculum")
    print("getting courses")
    import json

    courses = fetch_courses(request.content)

    with open("courses.json", "w", encoding="utf-8") as f:

        json.dump(courses, f, ensure_ascii=False, indent=4)